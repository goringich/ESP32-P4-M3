#!/usr/bin/env python3
"""Independent Project Chrono cross-check for the spherical robot."""

from __future__ import annotations

import argparse
import hashlib
from importlib import metadata
import json
import math
from pathlib import Path
import sys
from typing import Any


SIM_ROOT = Path(__file__).resolve().parent
ROBOT_ROOT = SIM_ROOT.parent
DIMENSIONS_PATH = ROBOT_ROOT / "config" / "dimensions.json"
SIMULATION_PATH = SIM_ROOT / "config.json"
if str(ROBOT_ROOT) not in sys.path:
  sys.path.insert(0, str(ROBOT_ROOT))

from calculations import load_config, sizing_report  # noqa: E402


def sha256(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
  value = json.loads(path.read_text(encoding="utf-8"))
  if not isinstance(value, dict):
    raise ValueError(f"{path} must contain an object")
  return value


def vector_length(vector: Any) -> float:
  return math.sqrt(float(vector.x) ** 2 + float(vector.y) ** 2 + float(vector.z) ** 2)


def build_system(
  chrono: Any,
  dimensions: dict[str, Any],
  simulation: dict[str, Any],
  *,
  ballast_mass_g: float,
  arm_mm: float,
  friction_mu: float,
) -> tuple[Any, Any, Any, Any]:
  report = sizing_report(dimensions)
  radius_m = float(dimensions["sphere_outer_diameter_mm"]) / 2000.0
  body_mass_kg = float(report["mass"]["body_mass_excluding_ballast_g_estimate"]) / 1000.0
  inertia_factor = float(simulation["body_inertia_factor_nominal"])
  body_inertia = inertia_factor * body_mass_kg * radius_m**2

  system = chrono.ChSystemNSC()
  system.SetGravitationalAcceleration(
    chrono.ChVector3d(0.0, -float(simulation["gravity_m_s2"]), 0.0)
  )
  system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

  floor_material = chrono.ChContactMaterialNSC()
  floor_material.SetFriction(float(friction_mu))
  shell_material = chrono.ChContactMaterialNSC()
  shell_material.SetFriction(float(friction_mu))

  floor = chrono.ChBodyEasyBox(
    4.0,
    0.10,
    4.0,
    1000.0,
    False,
    True,
    floor_material,
  )
  floor.SetFixed(True)
  floor.SetPos(chrono.ChVector3d(0.0, -0.05, 0.0))
  system.Add(floor)

  shell = chrono.ChBodyEasySphere(
    radius_m,
    1000.0,
    False,
    True,
    shell_material,
  )
  shell.SetMass(body_mass_kg)
  shell.SetInertiaXX(
    chrono.ChVector3d(body_inertia, body_inertia, body_inertia)
  )
  shell.SetPos(chrono.ChVector3d(0.0, radius_m, 0.0))
  system.Add(shell)

  pendulum_mass_kg = (
    float(ballast_mass_g)
    + float(simulation["pendulum_extra_mass_g_assumed"])
  ) / 1000.0
  ballast_radius_m = 0.02
  pendulum = chrono.ChBodyEasySphere(
    ballast_radius_m,
    1000.0,
    False,
    False,
  )
  pendulum.SetMass(pendulum_mass_kg)
  point_inertia = 0.4 * pendulum_mass_kg * ballast_radius_m**2
  pendulum.SetInertiaXX(
    chrono.ChVector3d(point_inertia, point_inertia, point_inertia)
  )
  arm_m = float(arm_mm) / 1000.0
  pendulum.SetPos(
    chrono.ChVector3d(0.0, radius_m - arm_m, 0.0)
  )
  system.Add(pendulum)

  motor = chrono.ChLinkMotorRotationTorque()
  motor.Initialize(
    pendulum,
    shell,
    chrono.ChFramed(chrono.ChVector3d(0.0, radius_m, 0.0)),
  )
  torque_function = chrono.ChFunctionConst(0.0)
  motor.SetTorqueFunction(torque_function)
  system.AddLink(motor)
  return system, shell, motor, torque_function


def execute_scenario(
  *,
  chrono: Any,
  dimensions: dict[str, Any],
  simulation: dict[str, Any],
  ballast_mass_g: float,
  arm_mm: float,
  friction_mu: float,
  torque_sign: float = 1.0,
) -> dict[str, Any]:
  system, shell, motor, torque_function = build_system(
    chrono,
    dimensions,
    simulation,
    ballast_mass_g=ballast_mass_g,
    arm_mm=arm_mm,
    friction_mu=friction_mu,
  )
  radius_m = float(dimensions["sphere_outer_diameter_mm"]) / 2000.0
  motor_torque_nm = float(dimensions["tt_motor_torque_nm_PLACEHOLDER"])
  no_load_rad_s = (
    float(dimensions["tt_motor_speed_rpm_PLACEHOLDER"])
    * 2.0
    * math.pi
    / 60.0
  )
  dt_s = 0.001
  settle_steps = 300
  pulse_steps = 450
  coast_steps = 650

  for _ in range(settle_steps):
    torque_function.SetConstant(0.0)
    system.DoStepDynamics(dt_s)

  initial_x = float(shell.GetPos().x)
  initial_y = float(shell.GetPos().y)
  contact_steps = 0
  peak_contact_force_n = 0.0
  peak_motor_torque_nm = 0.0
  peak_motor_speed_rad_s = 0.0
  maximum_abs_motor_angle_rad = 0.0
  minimum_center_y_m = initial_y
  maximum_center_y_m = initial_y
  finite = True

  for index in range(pulse_steps + coast_steps):
    motor_speed = abs(float(motor.GetMotorAngleDt()))
    available_torque = motor_torque_nm * max(
      0.0,
      1.0 - min(1.0, motor_speed / no_load_rad_s),
    )
    logical_requested = (
      torque_sign * 0.75 * motor_torque_nm
      if index < pulse_steps
      else 0.0
    )
    logical_applied = max(
      -available_torque,
      min(available_torque, logical_requested),
    )
    # Chrono uses Y-up here and the motor spindle is +Z. Negating maps the
    # logical positive torque to the same rolling-X convention as the MuJoCo
    # Z-up/+Y-hinge model.
    torque_function.SetConstant(-logical_applied)
    peak_motor_torque_nm = max(
      peak_motor_torque_nm,
      abs(logical_applied),
    )

    system.DoStepDynamics(dt_s)

    position = shell.GetPos()
    velocity = shell.GetLinVel()
    angle = float(motor.GetMotorAngle())
    speed = abs(float(motor.GetMotorAngleDt()))
    contact_force = shell.GetContactForce()
    contact_count = int(system.GetNumContacts())

    values = (
      float(position.x),
      float(position.y),
      float(position.z),
      float(velocity.x),
      float(velocity.y),
      float(velocity.z),
      angle,
      speed,
    )
    finite = finite and all(math.isfinite(value) for value in values)
    if contact_count > 0:
      contact_steps += 1
    peak_contact_force_n = max(
      peak_contact_force_n,
      vector_length(contact_force),
    )
    peak_motor_speed_rad_s = max(
      peak_motor_speed_rad_s,
      speed,
    )
    maximum_abs_motor_angle_rad = max(
      maximum_abs_motor_angle_rad,
      abs(angle),
    )
    minimum_center_y_m = min(minimum_center_y_m, float(position.y))
    maximum_center_y_m = max(maximum_center_y_m, float(position.y))

  final_x = float(shell.GetPos().x)
  final_y = float(shell.GetPos().y)
  displacement_m = final_x - initial_x
  contact_fraction = contact_steps / (pulse_steps + coast_steps)

  checks = {
    "finite_state": finite,
    "floor_contact_fraction_ok": contact_fraction >= 0.95,
    "sphere_height_bound_ok": (
      minimum_center_y_m >= radius_m - 0.010
      and maximum_center_y_m <= radius_m + 0.020
    ),
    "contact_force_observed": peak_contact_force_n > 0.0,
  }
  return {
    "inputs": {
      "ballast_mass_g": float(ballast_mass_g),
      "arm_mm": float(arm_mm),
      "friction_mu": float(friction_mu),
      "torque_sign": float(torque_sign),
    },
    "metrics": {
      "initial_x_m": initial_x,
      "final_x_m": final_x,
      "displacement_m": displacement_m,
      "initial_center_y_m": initial_y,
      "final_center_y_m": final_y,
      "minimum_center_y_m": minimum_center_y_m,
      "maximum_center_y_m": maximum_center_y_m,
      "floor_contact_fraction": contact_fraction,
      "peak_contact_force_n": peak_contact_force_n,
      "peak_applied_motor_torque_nm": peak_motor_torque_nm,
      "peak_motor_speed_rad_s": peak_motor_speed_rad_s,
      "maximum_absolute_pendulum_deg": math.degrees(
        maximum_abs_motor_angle_rad
      ),
    },
    "checks": checks,
    "passed": all(checks.values()),
  }


def symmetry_check(
  positive: dict[str, Any],
  negative: dict[str, Any],
) -> dict[str, Any]:
  pos = float(positive["metrics"]["displacement_m"])
  neg = float(negative["metrics"]["displacement_m"])
  magnitude = max(abs(pos), abs(neg))
  error = (
    abs(abs(pos) - abs(neg)) / magnitude
    if magnitude > 1e-12
    else float("inf")
  )
  checks = {
    "nonzero_response": magnitude >= 1e-5,
    "opposite_direction": pos * neg < 0.0,
    "symmetric_magnitude_within_15pct": error <= 0.15,
  }
  return {
    "positive_displacement_m": pos,
    "negative_displacement_m": neg,
    "relative_magnitude_error": error,
    "checks": checks,
    "passed": all(checks.values()),
  }


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "--output",
    type=Path,
    default=ROBOT_ROOT / "exports" / "simulation" / "chrono_execution.json",
  )
  args = parser.parse_args()

  try:
    import pychrono.core as chrono
  except ImportError as error:
    print(json.dumps({
      "status": "CROSSCHECK_BACKEND_BLOCKED",
      "backend": "project-chrono",
      "error": str(error),
      "physical_accepted": False,
    }))
    return 3

  dimensions = load_config(DIMENSIONS_PATH)
  simulation = load_json(SIMULATION_PATH)
  scenarios = []
  for ballast_mass_g in dimensions["ballast_variants_g"]:
    for arm_mm in dimensions["pendulum_arm_radii_mm"]:
      for friction_mu in simulation["static_friction_mu_values"]:
        scenarios.append(
          execute_scenario(
            chrono=chrono,
            dimensions=dimensions,
            simulation=simulation,
            ballast_mass_g=float(ballast_mass_g),
            arm_mm=float(arm_mm),
            friction_mu=float(friction_mu),
          )
        )

  nominal = {
    "ballast_mass_g": float(dimensions["ballast_mass_g"]),
    "arm_mm": float(dimensions["pendulum_arm_mm"]),
    "friction_mu": float(simulation["static_friction_mu_values"][1]),
  }
  positive = execute_scenario(
    chrono=chrono,
    dimensions=dimensions,
    simulation=simulation,
    **nominal,
    torque_sign=1.0,
  )
  negative = execute_scenario(
    chrono=chrono,
    dimensions=dimensions,
    simulation=simulation,
    **nominal,
    torque_sign=-1.0,
  )
  symmetry = symmetry_check(positive, negative)
  failed = [
    index
    for index, scenario in enumerate(scenarios)
    if not scenario["passed"]
  ]
  passed = not failed and symmetry["passed"]
  try:
    version = metadata.version("pychrono")
  except metadata.PackageNotFoundError:
    version = "unknown"

  payload = {
    "schema_version": "2026-09-21.spherical-robot-chrono-execution.v1",
    "status": "PASS" if passed else "FAIL",
    "evidence_state": (
      "INDEPENDENT_DYNAMICS_CROSSCHECK_PASS"
      if passed
      else "INDEPENDENT_DYNAMICS_CROSSCHECK_FAIL"
    ),
    "design_verdict": "PROVISIONAL",
    "physical_accepted": False,
    "backend": {
      "name": "project-chrono",
      "version": version,
      "contact_method": "NSC",
      "collision_system": "BULLET",
    },
    "source": {
      "project_revision": dimensions.get("project_revision"),
      "dimensions_sha256": sha256(DIMENSIONS_PATH),
      "simulation_config_sha256": sha256(SIMULATION_PATH),
    },
    "scenario_count": len(scenarios),
    "failed_scenario_indexes": failed,
    "scenarios": scenarios,
    "symmetry_check": symmetry,
    "limitations": [
      "independent Chrono model uses a reduced rigid pendulum-body proxy rather than exact printed internal geometry",
      "canonical component and motor inputs still contain PLACEHOLDER/ASSUMED values",
      "magnitude agreement is evaluated separately against MuJoCo; neither solver is physical acceptance",
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
    "backend": payload["backend"],
    "scenario_count": payload["scenario_count"],
    "failed_scenarios": len(failed),
    "symmetry_passed": symmetry["passed"],
    "output": str(args.output),
  }))
  return 0 if passed else 1


if __name__ == "__main__":
  raise SystemExit(main())
