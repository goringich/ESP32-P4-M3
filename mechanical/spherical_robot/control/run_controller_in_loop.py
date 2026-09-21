#!/usr/bin/env python3
"""Run the production-intended pure-C spherical controller against MuJoCo."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
from typing import Any


CONTROL_ROOT = Path(__file__).resolve().parent
ROBOT_ROOT = CONTROL_ROOT.parent
SIM_ROOT = ROBOT_ROOT / "simulation"
DIMENSIONS_PATH = ROBOT_ROOT / "config" / "dimensions.json"
SIMULATION_PATH = SIM_ROOT / "config.json"
CONTROL_CONFIG_PATH = CONTROL_ROOT / "config.json"
if str(SIM_ROOT) not in sys.path:
  sys.path.insert(0, str(SIM_ROOT))

from mujoco_model import build_xml  # noqa: E402


class CilError(RuntimeError):
  pass


class ControllerParams(ctypes.Structure):
  _fields_ = [
    ("sphere_radius_m", ctypes.c_float),
    ("speed_to_tilt_gain_rad_per_m_s", ctypes.c_float),
    ("maximum_tilt_rad", ctypes.c_float),
    ("pendulum_kp_nm_per_rad", ctypes.c_float),
    ("pendulum_kd_nms_per_rad", ctypes.c_float),
    ("motor_torque_nm", ctypes.c_float),
    ("motor_no_load_rad_s", ctypes.c_float),
  ]


class ControllerSensors(ctypes.Structure):
  _fields_ = [
    ("shell_roll_angle_rad", ctypes.c_float),
    ("shell_gyro_y_rad_s", ctypes.c_float),
    ("pendulum_relative_angle_rad", ctypes.c_float),
    ("pendulum_relative_speed_rad_s", ctypes.c_float),
  ]


class ControllerTarget(ctypes.Structure):
  _fields_ = [
    ("target_shell_speed_m_s", ctypes.c_float),
    ("target_steering_angle_rad", ctypes.c_float),
  ]


class ControllerOutput(ctypes.Structure):
  _fields_ = [
    ("estimated_shell_speed_m_s", ctypes.c_float),
    ("speed_error_m_s", ctypes.c_float),
    ("desired_pendulum_angle_rad", ctypes.c_float),
    ("absolute_pendulum_angle_rad", ctypes.c_float),
    ("absolute_pendulum_speed_rad_s", ctypes.c_float),
    ("available_motor_torque_nm", ctypes.c_float),
    ("pendulum_torque_nm", ctypes.c_float),
    ("pendulum_command_normalized", ctypes.c_float),
    ("steering_command_normalized", ctypes.c_float),
    ("torque_saturated", ctypes.c_bool),
    ("valid", ctypes.c_bool),
  ]


def sha256(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
  value = json.loads(path.read_text(encoding="utf-8"))
  if not isinstance(value, dict):
    raise CilError(f"{path} must contain a JSON object")
  return value


def load_controller(library_path: Path) -> Any:
  if not library_path.is_file():
    raise CilError(f"controller library missing: {library_path}")
  library = ctypes.CDLL(str(library_path))
  library.spherical_control_validate_params.argtypes = [
    ctypes.POINTER(ControllerParams),
  ]
  library.spherical_control_validate_params.restype = ctypes.c_bool
  library.spherical_control_step.argtypes = [
    ctypes.POINTER(ControllerParams),
    ctypes.POINTER(ControllerSensors),
    ctypes.POINTER(ControllerTarget),
    ctypes.POINTER(ControllerOutput),
  ]
  library.spherical_control_step.restype = None
  return library


def controller_params(
  dimensions: dict[str, Any],
  simulation: dict[str, Any],
) -> ControllerParams:
  cfg = simulation["controller"]
  return ControllerParams(
    sphere_radius_m=float(dimensions["sphere_outer_diameter_mm"]) / 2000.0,
    speed_to_tilt_gain_rad_per_m_s=float(
      cfg["speed_to_tilt_gain_rad_per_m_s"]
    ),
    maximum_tilt_rad=math.radians(float(cfg["maximum_tilt_deg"])),
    pendulum_kp_nm_per_rad=float(cfg["pendulum_kp_nm_per_rad"]),
    pendulum_kd_nms_per_rad=float(cfg["pendulum_kd_nms_per_rad"]),
    motor_torque_nm=float(dimensions["tt_motor_torque_nm_PLACEHOLDER"]),
    motor_no_load_rad_s=(
      float(dimensions["tt_motor_speed_rpm_PLACEHOLDER"])
      * 2.0
      * math.pi
      / 60.0
    ),
  )


def named_id(mujoco: Any, model: Any, object_type: Any, name: str) -> int:
  value = int(mujoco.mj_name2id(model, object_type, name))
  if value < 0:
    raise CilError(f"MuJoCo object missing: {name}")
  return value


def wrapped_shell_roll_y(data: Any, free_qpos: int) -> float:
  w = float(data.qpos[free_qpos + 3])
  x = float(data.qpos[free_qpos + 4])
  y = float(data.qpos[free_qpos + 5])
  z = float(data.qpos[free_qpos + 6])
  numerator = 2.0 * (w * y + x * z)
  denominator = 1.0 - 2.0 * (y * y + z * z)
  return math.atan2(numerator, denominator)


def unwrap_angle(previous: float, wrapped: float) -> float:
  candidate = wrapped
  while candidate - previous > math.pi:
    candidate -= 2.0 * math.pi
  while candidate - previous < -math.pi:
    candidate += 2.0 * math.pi
  return candidate


def execute_scenario(
  *,
  mujoco: Any,
  np: Any,
  controller: Any,
  params: ControllerParams,
  dimensions: dict[str, Any],
  control_config: dict[str, Any],
  ballast_mass_g: float,
  arm_mm: float,
  friction_mu: float,
  target_sign: float,
) -> dict[str, Any]:
  model = mujoco.MjModel.from_xml_string(
    build_xml(
      ballast_mass_g=ballast_mass_g,
      arm_mm=arm_mm,
      friction_mu=friction_mu,
    )
  )
  data = mujoco.MjData(model)

  sphere_body = named_id(mujoco, model, mujoco.mjtObj.mjOBJ_BODY, "sphere")
  floor_geom = named_id(mujoco, model, mujoco.mjtObj.mjOBJ_GEOM, "floor")
  shell_geom = named_id(
    mujoco,
    model,
    mujoco.mjtObj.mjOBJ_GEOM,
    "shell_contact",
  )
  free_joint = named_id(
    mujoco,
    model,
    mujoco.mjtObj.mjOBJ_JOINT,
    "sphere_free",
  )
  pendulum_joint = named_id(
    mujoco,
    model,
    mujoco.mjtObj.mjOBJ_JOINT,
    "pendulum_hinge",
  )
  motor = named_id(
    mujoco,
    model,
    mujoco.mjtObj.mjOBJ_ACTUATOR,
    "pendulum_motor",
  )
  gyro_sensor = named_id(
    mujoco,
    model,
    mujoco.mjtObj.mjOBJ_SENSOR,
    "imu_gyro",
  )

  free_dof = int(model.jnt_dofadr[free_joint])
  free_qpos = int(model.jnt_qposadr[free_joint])
  pendulum_dof = int(model.jnt_dofadr[pendulum_joint])
  pendulum_qpos = int(model.jnt_qposadr[pendulum_joint])
  gyro_adr = int(model.sensor_adr[gyro_sensor])
  gyro_dim = int(model.sensor_dim[gyro_sensor])
  if gyro_dim != 3:
    raise CilError(f"imu_gyro dimension must be 3, got {gyro_dim}")

  dt = float(model.opt.timestep)
  control_period = float(control_config["control_period_s"])
  control_steps = max(1, int(round(control_period / dt)))
  settle_steps = int(round(0.30 / dt))
  command_steps = int(round(float(control_config["command_duration_s"]) / dt))
  coast_steps = int(round(float(control_config["coast_duration_s"]) / dt))
  target_speed = (
    target_sign * float(control_config["screening_target_speed_m_s"])
  )

  mujoco.mj_forward(model, data)
  for _ in range(settle_steps):
    data.ctrl[:] = 0.0
    mujoco.mj_step(model, data)

  initial_x = float(data.xpos[sphere_body][0])
  command = ControllerOutput()
  command.pendulum_torque_nm = 0.0
  finite = True
  contact_steps = 0
  unexpected_contacts = 0
  maximum_abs_pendulum = 0.0
  peak_torque = 0.0
  peak_command = 0.0
  saturated_ticks = 0
  control_ticks = 0
  tracking_samples: list[float] = []
  estimate_errors: list[float] = []
  coast_samples: list[float] = []
  shell_roll = wrapped_shell_roll_y(data, free_qpos)

  total_active_steps = command_steps + coast_steps
  tracking_start = int(command_steps * 0.75)

  for step in range(total_active_steps):
    if step % control_steps == 0:
      target = ControllerTarget(
        target_shell_speed_m_s=target_speed if step < command_steps else 0.0,
        target_steering_angle_rad=0.0,
      )
      gyro_y = float(data.sensordata[gyro_adr + 1])
      shell_roll = unwrap_angle(
        shell_roll,
        wrapped_shell_roll_y(data, free_qpos),
      )
      sensors = ControllerSensors(
        shell_roll_angle_rad=shell_roll,
        shell_gyro_y_rad_s=gyro_y,
        pendulum_relative_angle_rad=float(data.qpos[pendulum_qpos]),
        pendulum_relative_speed_rad_s=float(data.qvel[pendulum_dof]),
      )
      command = ControllerOutput()
      controller.spherical_control_step(
        ctypes.byref(params),
        ctypes.byref(sensors),
        ctypes.byref(target),
        ctypes.byref(command),
      )
      if not command.valid:
        raise CilError("controller returned invalid output")
      control_ticks += 1
      saturated_ticks += int(command.torque_saturated)

    data.ctrl[:] = 0.0
    data.ctrl[motor] = float(command.pendulum_torque_nm)
    mujoco.mj_step(model, data)

    actual_speed = float(data.qvel[free_dof])
    estimated_speed = float(command.estimated_shell_speed_m_s)
    finite = finite and bool(
      np.isfinite(data.qpos).all()
      and np.isfinite(data.qvel).all()
      and np.isfinite(data.qacc).all()
      and math.isfinite(float(command.pendulum_torque_nm))
    )
    maximum_abs_pendulum = max(
      maximum_abs_pendulum,
      abs(float(command.absolute_pendulum_angle_rad)),
    )
    peak_torque = max(
      peak_torque,
      abs(float(command.pendulum_torque_nm)),
    )
    peak_command = max(
      peak_command,
      abs(float(command.pendulum_command_normalized)),
    )
    estimate_errors.append(abs(actual_speed - estimated_speed))

    if tracking_start <= step < command_steps:
      tracking_samples.append(actual_speed)
    if step >= command_steps + int(coast_steps * 0.5):
      coast_samples.append(actual_speed)

    floor_seen = False
    for contact_index in range(int(data.ncon)):
      contact = data.contact[contact_index]
      pair = {int(contact.geom1), int(contact.geom2)}
      if pair == {floor_geom, shell_geom}:
        floor_seen = True
      else:
        unexpected_contacts += 1
    if floor_seen:
      contact_steps += 1

  if not tracking_samples:
    raise CilError("tracking window contains no samples")
  mean_tracking_speed = sum(tracking_samples) / len(tracking_samples)
  mean_coast_speed = (
    sum(coast_samples) / len(coast_samples)
    if coast_samples
    else float(data.qvel[free_dof])
  )
  tracking_fraction = (
    abs(mean_tracking_speed) / abs(target_speed)
    if target_speed
    else 0.0
  )
  direction_ok = mean_tracking_speed * target_speed > 0.0
  contact_fraction = contact_steps / total_active_steps
  mean_estimate_error = sum(estimate_errors) / len(estimate_errors)

  checks = {
    "finite_state": finite,
    "tracking_direction_ok": direction_ok,
    "tracking_fraction_ok": (
      tracking_fraction
      >= float(control_config["minimum_tracking_fraction"])
    ),
    "pendulum_angle_bound_ok": (
      math.degrees(maximum_abs_pendulum)
      <= float(control_config["maximum_absolute_pendulum_deg"])
    ),
    "motor_torque_bound_ok": (
      peak_torque <= float(params.motor_torque_nm) + 1.0e-6
    ),
    "normalized_command_bound_ok": peak_command <= 1.000001,
    "floor_contact_fraction_ok": (
      contact_fraction
      >= float(control_config["minimum_floor_contact_fraction"])
    ),
    "unexpected_contacts_absent": unexpected_contacts == 0,
  }

  return {
    "inputs": {
      "ballast_mass_g": float(ballast_mass_g),
      "arm_mm": float(arm_mm),
      "friction_mu": float(friction_mu),
      "target_speed_m_s": target_speed,
    },
    "metrics": {
      "displacement_m": float(data.xpos[sphere_body][0]) - initial_x,
      "mean_tracking_speed_m_s": mean_tracking_speed,
      "tracking_fraction": tracking_fraction,
      "mean_coast_speed_m_s": mean_coast_speed,
      "maximum_absolute_pendulum_deg": math.degrees(maximum_abs_pendulum),
      "peak_motor_torque_nm": peak_torque,
      "peak_normalized_command": peak_command,
      "floor_contact_fraction": contact_fraction,
      "unexpected_contact_count": unexpected_contacts,
      "mean_shell_speed_estimate_abs_error_m_s": mean_estimate_error,
      "controller_ticks": control_ticks,
      "torque_saturated_tick_fraction": (
        saturated_ticks / control_ticks
        if control_ticks
        else 0.0
      ),
    },
    "checks": checks,
    "passed": all(checks.values()),
  }


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument("--library", type=Path, required=True)
  parser.add_argument(
    "--output",
    type=Path,
    default=ROBOT_ROOT / "exports" / "simulation" / "controller_in_loop.json",
  )
  args = parser.parse_args()

  try:
    import mujoco
    import numpy as np
  except ImportError as error:
    print(json.dumps({
      "status": "CONTROLLER_IN_LOOP_BACKEND_BLOCKED",
      "error": str(error),
      "physical_accepted": False,
    }))
    return 3

  try:
    dimensions = read_json(DIMENSIONS_PATH)
    simulation = read_json(SIMULATION_PATH)
    control_config = read_json(CONTROL_CONFIG_PATH)
    controller = load_controller(args.library)
    params = controller_params(dimensions, simulation)
    if not controller.spherical_control_validate_params(ctypes.byref(params)):
      raise CilError("controller parameter contract rejected canonical parameters")

    scenarios = []
    for ballast_mass_g in dimensions["ballast_variants_g"]:
      for arm_mm in dimensions["pendulum_arm_radii_mm"]:
        for friction_mu in simulation["static_friction_mu_values"]:
          for target_sign in (-1.0, 1.0):
            scenarios.append(
              execute_scenario(
                mujoco=mujoco,
                np=np,
                controller=controller,
                params=params,
                dimensions=dimensions,
                control_config=control_config,
                ballast_mass_g=float(ballast_mass_g),
                arm_mm=float(arm_mm),
                friction_mu=float(friction_mu),
                target_sign=target_sign,
              )
            )
  except (OSError, ValueError, json.JSONDecodeError, CilError) as error:
    print(json.dumps({
      "status": "CONTROLLER_IN_LOOP_BLOCKED",
      "error": str(error),
      "physical_accepted": False,
    }))
    return 3

  failures = [
    index
    for index, scenario in enumerate(scenarios)
    if not scenario["passed"]
  ]
  passed = not failures
  policy = control_config["evidence_policy"]
  payload = {
    "schema_version": "2026-09-21.spherical-controller-in-loop-result.v1",
    "status": "PASS" if passed else "FAIL",
    "evidence_state": (
      policy["pass_state"]
      if passed
      else "CONTROLLER_IN_LOOP_SCREENING_FAIL"
    ),
    "design_verdict": "PROVISIONAL",
    "physical_accepted": False,
    "backend": {
      "plant": f"mujoco-{mujoco.__version__}",
      "python": platform.python_version(),
      "numpy": np.__version__,
      "controller_implementation": "pure-c-components/spherical_control",
    },
    "source": {
      "dimensions_sha256": sha256(DIMENSIONS_PATH),
      "simulation_config_sha256": sha256(SIMULATION_PATH),
      "control_config_sha256": sha256(CONTROL_CONFIG_PATH),
      "controller_source_sha256": sha256(
        ROBOT_ROOT.parent.parent
        / "components"
        / "spherical_control"
        / "src"
        / "spherical_control.c"
      ),
    },
    "scenario_count": len(scenarios),
    "failed_scenario_indexes": failures,
    "scenarios": scenarios,
    "status_contract": control_config["status"],
    "limitations": control_config["limitations"],
  }
  args.output.parent.mkdir(parents=True, exist_ok=True)
  args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

  tracking = [
    float(row["metrics"]["tracking_fraction"])
    for row in scenarios
  ]
  estimate_error = [
    float(row["metrics"]["mean_shell_speed_estimate_abs_error_m_s"])
    for row in scenarios
  ]
  print(json.dumps({
    "status": payload["status"],
    "evidence_state": payload["evidence_state"],
    "scenario_count": len(scenarios),
    "failed_scenarios": len(failures),
    "minimum_tracking_fraction_observed": min(tracking),
    "maximum_tracking_fraction_observed": max(tracking),
    "maximum_mean_speed_estimate_error_m_s": max(estimate_error),
    "physical_accepted": False,
    "output": str(args.output),
  }))
  return 0 if passed else 1


if __name__ == "__main__":
  raise SystemExit(main())
