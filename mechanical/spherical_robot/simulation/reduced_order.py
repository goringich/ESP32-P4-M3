#!/usr/bin/env python3
"""Auditable reduced-order dynamics for the pendulum-driven spherical robot.

The plant is intentionally planar. It enforces rolling kinematics and reports a
friction margin; a negative margin means the no-slip assumption is invalid for
that step and the scenario must be escalated to a contact solver.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
import sys
from typing import Callable


SIM_ROOT = Path(__file__).resolve().parent
ROBOT_ROOT = SIM_ROOT.parent
if str(ROBOT_ROOT) not in sys.path:
  sys.path.insert(0, str(ROBOT_ROOT))

from calculations import load_config, sizing_report  # noqa: E402


@dataclass(frozen=True)
class Parameters:
  radius_m: float
  body_mass_kg: float
  body_inertia_kg_m2: float
  pendulum_mass_kg: float
  pendulum_length_m: float
  gravity_m_s2: float
  static_friction_mu: float
  rolling_drag_ns_per_m: float
  pendulum_damping_nms: float
  motor_torque_nm: float
  motor_no_load_rad_s: float


@dataclass(frozen=True)
class State:
  x_m: float = 0.0
  v_m_s: float = 0.0
  theta_rad: float = 0.0
  omega_rad_s: float = 0.0


@dataclass(frozen=True)
class Diagnostics:
  applied_motor_torque_nm: float
  available_motor_torque_nm: float
  relative_motor_speed_rad_s: float
  contact_force_n: float
  normal_force_n: float
  friction_margin_n: float
  determinant: float


Controller = Callable[[float, State, Parameters], float]


def load_simulation_config(path: Path = SIM_ROOT / "config.json") -> dict:
  value = json.loads(path.read_text(encoding="utf-8"))
  if not isinstance(value, dict):
    raise ValueError("simulation config must be an object")
  return value


def clamp(value: float, low: float, high: float) -> float:
  return max(low, min(high, value))


def build_parameters(
  *,
  dimensions: dict | None = None,
  simulation: dict | None = None,
  ballast_mass_g: float | None = None,
  arm_mm: float | None = None,
  friction_mu: float | None = None,
  inertia_factor: float | None = None,
) -> Parameters:
  dimensions = dimensions or load_config()
  simulation = simulation or load_simulation_config()
  report = sizing_report(dimensions)

  selected_ballast_g = float(
    dimensions["ballast_mass_g"] if ballast_mass_g is None else ballast_mass_g
  )
  extra_mass_g = float(simulation["pendulum_extra_mass_g_assumed"])
  body_mass_kg = float(report["mass"]["body_mass_excluding_ballast_g_estimate"]) / 1000.0
  radius_m = float(dimensions["sphere_outer_diameter_mm"]) / 2000.0
  selected_inertia_factor = float(
    simulation["body_inertia_factor_nominal"]
    if inertia_factor is None
    else inertia_factor
  )
  body_inertia = selected_inertia_factor * body_mass_kg * radius_m**2
  length_m = float(dimensions["pendulum_arm_mm"] if arm_mm is None else arm_mm) / 1000.0
  mu = float(
    simulation["static_friction_mu_values"][1]
    if friction_mu is None
    else friction_mu
  )
  motor_rpm = float(dimensions["tt_motor_speed_rpm_PLACEHOLDER"])
  motor_torque = float(dimensions["tt_motor_torque_nm_PLACEHOLDER"])
  if min(body_mass_kg, radius_m, length_m, motor_rpm, motor_torque, mu) <= 0:
    raise ValueError("physical parameters must be positive")

  return Parameters(
    radius_m=radius_m,
    body_mass_kg=body_mass_kg,
    body_inertia_kg_m2=body_inertia,
    pendulum_mass_kg=(selected_ballast_g + extra_mass_g) / 1000.0,
    pendulum_length_m=length_m,
    gravity_m_s2=float(simulation["gravity_m_s2"]),
    static_friction_mu=mu,
    rolling_drag_ns_per_m=float(simulation["rolling_drag_ns_per_m"]),
    pendulum_damping_nms=float(simulation["pendulum_damping_nms"]),
    motor_torque_nm=motor_torque,
    motor_no_load_rad_s=motor_rpm * 2.0 * math.pi / 60.0,
  )


def available_motor_torque(params: Parameters, state: State) -> tuple[float, float]:
  shell_omega = state.v_m_s / params.radius_m
  relative_speed = state.omega_rad_s - shell_omega
  speed_fraction = abs(relative_speed) / params.motor_no_load_rad_s
  available = params.motor_torque_nm * max(0.0, 1.0 - speed_fraction)
  return available, relative_speed


def derivatives(
  state: State,
  params: Parameters,
  requested_torque_nm: float,
) -> tuple[State, Diagnostics]:
  available, relative_speed = available_motor_torque(params, state)
  torque = clamp(requested_torque_nm, -available, available)

  theta = state.theta_rad
  omega = state.omega_rad_s
  m = params.pendulum_mass_kg
  length = params.pendulum_length_m

  effective_body_mass = (
    params.body_mass_kg
    + params.body_inertia_kg_m2 / params.radius_m**2
  )
  a11 = effective_body_mass + m
  a12 = m * length * math.cos(theta)
  a22 = m * length**2

  rhs1 = (
    -torque / params.radius_m
    - params.rolling_drag_ns_per_m * state.v_m_s
    + m * length * math.sin(theta) * omega**2
  )
  rhs2 = (
    torque
    - params.pendulum_damping_nms * omega
    - m * params.gravity_m_s2 * length * math.sin(theta)
  )

  determinant = a11 * a22 - a12**2
  if determinant <= 1e-12:
    raise ValueError("singular reduced-order mass matrix")

  acceleration = (rhs1 * a22 - a12 * rhs2) / determinant
  angular_acceleration = (a11 * rhs2 - a12 * rhs1) / determinant

  pendulum_horizontal_acceleration = length * (
    math.cos(theta) * angular_acceleration
    - math.sin(theta) * omega**2
  )
  pendulum_vertical_acceleration = length * (
    math.sin(theta) * angular_acceleration
    + math.cos(theta) * omega**2
  )
  contact_force = (
    (params.body_mass_kg + m) * acceleration
    + m * pendulum_horizontal_acceleration
  )
  normal_force = (
    (params.body_mass_kg + m) * params.gravity_m_s2
    + m * pendulum_vertical_acceleration
  )
  normal_force = max(0.0, normal_force)
  friction_margin = params.static_friction_mu * normal_force - abs(contact_force)

  return (
    State(
      x_m=state.v_m_s,
      v_m_s=acceleration,
      theta_rad=state.omega_rad_s,
      omega_rad_s=angular_acceleration,
    ),
    Diagnostics(
      applied_motor_torque_nm=torque,
      available_motor_torque_nm=available,
      relative_motor_speed_rad_s=relative_speed,
      contact_force_n=contact_force,
      normal_force_n=normal_force,
      friction_margin_n=friction_margin,
      determinant=determinant,
    ),
  )


def add_scaled(state: State, derivative: State, scale: float) -> State:
  return State(
    x_m=state.x_m + derivative.x_m * scale,
    v_m_s=state.v_m_s + derivative.v_m_s * scale,
    theta_rad=state.theta_rad + derivative.theta_rad * scale,
    omega_rad_s=state.omega_rad_s + derivative.omega_rad_s * scale,
  )


def rk4_step(
  t_s: float,
  state: State,
  dt_s: float,
  params: Parameters,
  controller: Controller,
) -> tuple[State, Diagnostics]:
  torque1 = controller(t_s, state, params)
  k1, diag = derivatives(state, params, torque1)

  state2 = add_scaled(state, k1, dt_s / 2.0)
  k2, _ = derivatives(
    state2,
    params,
    controller(t_s + dt_s / 2.0, state2, params),
  )

  state3 = add_scaled(state, k2, dt_s / 2.0)
  k3, _ = derivatives(
    state3,
    params,
    controller(t_s + dt_s / 2.0, state3, params),
  )

  state4 = add_scaled(state, k3, dt_s)
  k4, _ = derivatives(
    state4,
    params,
    controller(t_s + dt_s, state4, params),
  )

  next_state = State(
    x_m=state.x_m + dt_s * (k1.x_m + 2.0 * k2.x_m + 2.0 * k3.x_m + k4.x_m) / 6.0,
    v_m_s=state.v_m_s + dt_s * (k1.v_m_s + 2.0 * k2.v_m_s + 2.0 * k3.v_m_s + k4.v_m_s) / 6.0,
    theta_rad=state.theta_rad + dt_s * (k1.theta_rad + 2.0 * k2.theta_rad + 2.0 * k3.theta_rad + k4.theta_rad) / 6.0,
    omega_rad_s=state.omega_rad_s + dt_s * (k1.omega_rad_s + 2.0 * k2.omega_rad_s + 2.0 * k3.omega_rad_s + k4.omega_rad_s) / 6.0,
  )
  if not all(math.isfinite(value) for value in next_state.__dict__.values()):
    raise ValueError("non-finite reduced-order state")
  return next_state, diag


def total_energy_j(state: State, params: Parameters) -> float:
  m = params.pendulum_mass_kg
  length = params.pendulum_length_m
  translational = 0.5 * (
    params.body_mass_kg
    + m
    + params.body_inertia_kg_m2 / params.radius_m**2
  ) * state.v_m_s**2
  coupling = m * length * math.cos(state.theta_rad) * state.v_m_s * state.omega_rad_s
  pendulum_kinetic = 0.5 * m * length**2 * state.omega_rad_s**2
  potential = m * params.gravity_m_s2 * length * (1.0 - math.cos(state.theta_rad))
  return translational + coupling + pendulum_kinetic + potential


def speed_controller(
  target_speed_m_s: float,
  simulation: dict | None = None,
) -> Controller:
  simulation = simulation or load_simulation_config()
  cfg = simulation["controller"]
  gain = float(cfg["speed_to_tilt_gain_rad_per_m_s"])
  max_tilt = math.radians(float(cfg["maximum_tilt_deg"]))
  kp = float(cfg["pendulum_kp_nm_per_rad"])
  kd = float(cfg["pendulum_kd_nms_per_rad"])

  def control(_time: float, state: State, _params: Parameters) -> float:
    desired_theta = -clamp(gain * (target_speed_m_s - state.v_m_s), -max_tilt, max_tilt)
    return kp * (desired_theta - state.theta_rad) - kd * state.omega_rad_s

  return control


def simulate(
  *,
  params: Parameters,
  controller: Controller,
  duration_s: float,
  dt_s: float,
  initial_state: State = State(),
) -> dict:
  if duration_s <= 0 or dt_s <= 0 or dt_s > duration_s:
    raise ValueError("invalid integration interval")

  state = initial_state
  steps = int(math.ceil(duration_s / dt_s))
  min_friction_margin = float("inf")
  peak_contact_force = 0.0
  peak_normal_force = 0.0
  peak_torque = 0.0
  peak_relative_speed = 0.0
  max_abs_theta = abs(state.theta_rad)

  for index in range(steps):
    t_s = index * dt_s
    state, diag = rk4_step(t_s, state, dt_s, params, controller)
    min_friction_margin = min(min_friction_margin, diag.friction_margin_n)
    peak_contact_force = max(peak_contact_force, abs(diag.contact_force_n))
    peak_normal_force = max(peak_normal_force, diag.normal_force_n)
    peak_torque = max(peak_torque, abs(diag.applied_motor_torque_nm))
    peak_relative_speed = max(peak_relative_speed, abs(diag.relative_motor_speed_rad_s))
    max_abs_theta = max(max_abs_theta, abs(state.theta_rad))

  return {
    "final_state": {
      "x_m": state.x_m,
      "v_m_s": state.v_m_s,
      "theta_rad": state.theta_rad,
      "omega_rad_s": state.omega_rad_s,
    },
    "metrics": {
      "minimum_friction_margin_n": min_friction_margin,
      "peak_contact_force_n": peak_contact_force,
      "peak_normal_force_n": peak_normal_force,
      "peak_motor_torque_nm": peak_torque,
      "peak_relative_motor_speed_rad_s": peak_relative_speed,
      "maximum_absolute_pendulum_deg": math.degrees(max_abs_theta),
    },
    "slip_risk": min_friction_margin < 0.0,
  }
