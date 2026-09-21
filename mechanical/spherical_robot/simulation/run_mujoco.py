#!/usr/bin/env python3
"""Execute the canonical spherical-robot model in MuJoCo.

This establishes multibody solver evidence only. It does not upgrade placeholder
inputs to measured truth and never sets physical acceptance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
from typing import Any


SIM_ROOT = Path(__file__).resolve().parent
ROBOT_ROOT = SIM_ROOT.parent
DIMENSIONS_PATH = ROBOT_ROOT / "config" / "dimensions.json"
SIMULATION_PATH = SIM_ROOT / "config.json"
if str(SIM_ROOT) not in sys.path:
  sys.path.insert(0, str(SIM_ROOT))

from mujoco_model import build_xml  # noqa: E402


def sha256(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
  value = json.loads(path.read_text(encoding="utf-8"))
  if not isinstance(value, dict):
    raise ValueError(f"{path} must contain an object")
  return value


def unresolved_inputs(dimensions: dict[str, Any], simulation: dict[str, Any]) -> list[str]:
  unresolved = {
    f"dimensions:{key}"
    for key, status in (dimensions.get("dimension_status") or {}).items()
    if status in {"PLACEHOLDER", "ASSUMED"}
  }
  unresolved.update(
    f"simulation:{key}"
    for key, status in (simulation.get("status") or {}).items()
    if status in {"PLACEHOLDER", "ASSUMED"}
  )
  return sorted(unresolved)


def execute_scenario(
  *,
  mujoco: Any,
  np: Any,
  dimensions: dict[str, Any],
  ballast_mass_g: float,
  arm_mm: float,
  friction_mu: float,
  torque_sign: float = 1.0,
) -> dict[str, Any]:
  xml = build_xml(
    ballast_mass_g=ballast_mass_g,
    arm_mm=arm_mm,
    friction_mu=friction_mu,
  )
  model = mujoco.MjModel.from_xml_string(xml)
  data = mujoco.MjData(model)

  sphere_body = mujoco.mj_name2id(
    model,
    mujoco.mjtObj.mjOBJ_BODY,
    "sphere",
  )
  floor_geom = mujoco.mj_name2id(
    model,
    mujoco.mjtObj.mjOBJ_GEOM,
    "floor",
  )
  shell_geom = mujoco.mj_name2id(
    model,
    mujoco.mjtObj.mjOBJ_GEOM,
    "shell_contact",
  )
  free_joint = mujoco.mj_name2id(
    model,
    mujoco.mjtObj.mjOBJ_JOINT,
    "sphere_free",
  )
  pendulum_joint = mujoco.mj_name2id(
    model,
    mujoco.mjtObj.mjOBJ_JOINT,
    "pendulum_hinge",
  )
  pendulum_motor = mujoco.mj_name2id(
    model,
    mujoco.mjtObj.mjOBJ_ACTUATOR,
    "pendulum_motor",
  )
  required_ids = {
    "sphere_body": sphere_body,
    "floor_geom": floor_geom,
    "shell_geom": shell_geom,
    "free_joint": free_joint,
    "pendulum_joint": pendulum_joint,
    "pendulum_motor": pendulum_motor,
  }
  if any(value < 0 for value in required_ids.values()):
    raise ValueError(f"MuJoCo model identity is incomplete: {required_ids}")

  free_dof = int(model.jnt_dofadr[free_joint])
  pendulum_dof = int(model.jnt_dofadr[pendulum_joint])
  pendulum_qpos = int(model.jnt_qposadr[pendulum_joint])

  radius_m = float(dimensions["sphere_outer_diameter_mm"]) / 2000.0
  nominal_motor_torque = float(dimensions["tt_motor_torque_nm_PLACEHOLDER"])
  no_load_rad_s = (
    float(dimensions["tt_motor_speed_rpm_PLACEHOLDER"])
    * 2.0
    * math.pi
    / 60.0
  )
  if min(radius_m, nominal_motor_torque, no_load_rad_s) <= 0:
    raise ValueError("motor and sphere parameters must be positive")

  settle_s = 0.30
  pulse_s = 0.45
  coast_s = 0.65
  timestep = float(model.opt.timestep)
  settle_steps = max(1, int(round(settle_s / timestep)))
  active_steps = max(1, int(round((pulse_s + coast_s) / timestep)))

  model.opt.disableflags = int(model.opt.disableflags)
  mujoco.mj_forward(model, data)
  for _ in range(settle_steps):
    data.ctrl[:] = 0.0
    mujoco.mj_step(model, data)

  initial_x = float(data.xpos[sphere_body][0])
  initial_z = float(data.xpos[sphere_body][2])
  contact_steps = 0
  max_penetration_m = 0.0
  max_normal_contact_force_n = 0.0
  peak_ctrl_nm = 0.0
  peak_pendulum_speed_rad_s = 0.0
  max_abs_pendulum_angle_rad = 0.0
  min_center_z_m = initial_z
  max_center_z_m = initial_z
  finite = True

  for index in range(active_steps):
    elapsed = index * timestep
    relative_speed = abs(float(data.qvel[pendulum_dof]))
    torque_speed_fraction = min(1.0, relative_speed / no_load_rad_s)
    available_torque = nominal_motor_torque * max(
      0.0,
      1.0 - torque_speed_fraction,
    )
    requested = (
      torque_sign * 0.75 * nominal_motor_torque
      if elapsed < pulse_s
      else 0.0
    )
    applied = max(-available_torque, min(available_torque, requested))
    data.ctrl[:] = 0.0
    data.ctrl[pendulum_motor] = applied
    peak_ctrl_nm = max(peak_ctrl_nm, abs(applied))

    mujoco.mj_step(model, data)
    finite = finite and bool(
      np.isfinite(data.qpos).all()
      and np.isfinite(data.qvel).all()
      and np.isfinite(data.qacc).all()
    )
    center_z = float(data.xpos[sphere_body][2])
    min_center_z_m = min(min_center_z_m, center_z)
    max_center_z_m = max(max_center_z_m, center_z)
    pendulum_speed = abs(float(data.qvel[pendulum_dof]))
    peak_pendulum_speed_rad_s = max(
      peak_pendulum_speed_rad_s,
      pendulum_speed,
    )
    pendulum_angle = abs(float(data.qpos[pendulum_qpos]))
    max_abs_pendulum_angle_rad = max(
      max_abs_pendulum_angle_rad,
      pendulum_angle,
    )

    floor_contact_seen = False
    for contact_index in range(int(data.ncon)):
      contact = data.contact[contact_index]
      pair = {int(contact.geom1), int(contact.geom2)}
      if pair != {floor_geom, shell_geom}:
        continue
      floor_contact_seen = True
      if float(contact.dist) < 0.0:
        max_penetration_m = max(
          max_penetration_m,
          -float(contact.dist),
        )
      force = np.zeros(6, dtype=float)
      mujoco.mj_contactForce(model, data, contact_index, force)
      max_normal_contact_force_n = max(
        max_normal_contact_force_n,
        abs(float(force[0])),
      )
    if floor_contact_seen:
      contact_steps += 1

  final_x = float(data.xpos[sphere_body][0])
  final_z = float(data.xpos[sphere_body][2])
  displacement_m = final_x - initial_x
  contact_fraction = contact_steps / active_steps

  checks = {
    "finite_state": finite,
    "floor_contact_fraction_ok": contact_fraction >= 0.95,
    "penetration_bound_ok": max_penetration_m <= 0.003,
    "sphere_height_bound_ok": (
      min_center_z_m >= radius_m - 0.006
      and max_center_z_m <= radius_m + 0.012
    ),
    "contact_force_observed": max_normal_contact_force_n > 0.0,
  }
  return {
    "inputs": {
      "ballast_mass_g": ballast_mass_g,
      "arm_mm": arm_mm,
      "friction_mu": friction_mu,
      "torque_sign": torque_sign,
    },
    "model": {
      "nq": int(model.nq),
      "nv": int(model.nv),
      "nu": int(model.nu),
      "timestep_s": timestep,
    },
    "metrics": {
      "initial_x_m": initial_x,
      "final_x_m": final_x,
      "displacement_m": displacement_m,
      "initial_center_z_m": initial_z,
      "final_center_z_m": final_z,
      "minimum_center_z_m": min_center_z_m,
      "maximum_center_z_m": max_center_z_m,
      "floor_contact_fraction": contact_fraction,
      "maximum_penetration_m": max_penetration_m,
      "maximum_normal_contact_force_n": max_normal_contact_force_n,
      "peak_applied_motor_torque_nm": peak_ctrl_nm,
      "peak_pendulum_speed_rad_s": peak_pendulum_speed_rad_s,
      "maximum_absolute_pendulum_deg": math.degrees(
        max_abs_pendulum_angle_rad
      ),
      "shell_angular_velocity_y_rad_s": float(
        data.qvel[free_dof + 4]
      ),
    },
    "checks": checks,
    "passed": all(checks.values()),
  }


def symmetry_check(positive: dict[str, Any], negative: dict[str, Any]) -> dict[str, Any]:
  pos = float(positive["metrics"]["displacement_m"])
  neg = float(negative["metrics"]["displacement_m"])
  magnitude = max(abs(pos), abs(neg))
  relative_magnitude_error = (
    abs(abs(pos) - abs(neg)) / magnitude
    if magnitude > 1e-12
    else float("inf")
  )
  opposite_direction = pos * neg < 0.0
  nonzero_response = magnitude >= 1e-5
  symmetric_magnitude = relative_magnitude_error <= 0.10
  checks = {
    "nonzero_response": nonzero_response,
    "opposite_direction": opposite_direction,
    "symmetric_magnitude_within_10pct": symmetric_magnitude,
  }
  return {
    "positive_displacement_m": pos,
    "negative_displacement_m": neg,
    "relative_magnitude_error": relative_magnitude_error,
    "checks": checks,
    "passed": all(checks.values()),
  }


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "--output",
    type=Path,
    default=ROBOT_ROOT / "exports" / "simulation" / "mujoco_execution.json",
  )
  args = parser.parse_args()

  try:
    import mujoco
    import numpy as np
  except ImportError as error:
    payload = {
      "status": "SIMULATION_BACKEND_BLOCKED",
      "backend": "mujoco",
      "error": str(error),
      "physical_accepted": False,
    }
    print(json.dumps(payload))
    return 3

  dimensions = load_json(DIMENSIONS_PATH)
  simulation = load_json(SIMULATION_PATH)
  scenarios = []
  for ballast_mass_g in dimensions["ballast_variants_g"]:
    for arm_mm in dimensions["pendulum_arm_radii_mm"]:
      for friction_mu in simulation["static_friction_mu_values"]:
        scenarios.append(
          execute_scenario(
            mujoco=mujoco,
            np=np,
            dimensions=dimensions,
            ballast_mass_g=float(ballast_mass_g),
            arm_mm=float(arm_mm),
            friction_mu=float(friction_mu),
          )
        )

  nominal_ballast = float(dimensions["ballast_mass_g"])
  nominal_arm = float(dimensions["pendulum_arm_mm"])
  nominal_mu = float(simulation["static_friction_mu_values"][1])
  positive = execute_scenario(
    mujoco=mujoco,
    np=np,
    dimensions=dimensions,
    ballast_mass_g=nominal_ballast,
    arm_mm=nominal_arm,
    friction_mu=nominal_mu,
    torque_sign=1.0,
  )
  negative = execute_scenario(
    mujoco=mujoco,
    np=np,
    dimensions=dimensions,
    ballast_mass_g=nominal_ballast,
    arm_mm=nominal_arm,
    friction_mu=nominal_mu,
    torque_sign=-1.0,
  )
  symmetry = symmetry_check(positive, negative)
  scenario_failures = [
    index
    for index, scenario in enumerate(scenarios)
    if not scenario["passed"]
  ]
  passed = not scenario_failures and symmetry["passed"]

  payload = {
    "schema_version": "2026-09-21.spherical-robot-mujoco-execution.v1",
    "status": "PASS" if passed else "FAIL",
    "evidence_state": (
      "PRIMARY_MULTIBODY_PASS"
      if passed
      else "PRIMARY_MULTIBODY_FAIL"
    ),
    "design_verdict": "PROVISIONAL",
    "physical_accepted": False,
    "backend": {
      "name": "mujoco",
      "version": str(mujoco.__version__),
      "python": platform.python_version(),
      "numpy": str(np.__version__),
    },
    "source": {
      "project_revision": dimensions.get("project_revision"),
      "dimensions_sha256": sha256(DIMENSIONS_PATH),
      "simulation_config_sha256": sha256(SIMULATION_PATH),
    },
    "scenario_count": len(scenarios),
    "failed_scenario_indexes": scenario_failures,
    "scenarios": scenarios,
    "symmetry_check": symmetry,
    "unresolved_inputs": unresolved_inputs(dimensions, simulation),
    "limitations": [
      "component envelopes and motor performance still include placeholder or assumed inputs",
      "contact model is rigid-body and does not model printed-shell compliance or TPU hysteresis",
      "motor torque-speed curve is a linear screening approximation based on current placeholder values",
      "steering/yaw performance is represented geometrically but is not yet a release-qualified steering controller study",
      "Project Chrono independent cross-check, FEA, HIL and physical tests remain separate evidence layers",
    ],
  }
  args.output.parent.mkdir(parents=True, exist_ok=True)
  args.output.write_text(
    json.dumps(payload, indent=2) + "\n",
    encoding="utf-8",
  )
  print(json.dumps({
    "status": payload["status"],
    "evidence_state": payload["evidence_state"],
    "design_verdict": payload["design_verdict"],
    "backend": payload["backend"],
    "scenario_count": payload["scenario_count"],
    "failed_scenarios": len(scenario_failures),
    "symmetry_passed": symmetry["passed"],
    "output": str(args.output),
  }))
  return 0 if passed else 1


if __name__ == "__main__":
  raise SystemExit(main())
