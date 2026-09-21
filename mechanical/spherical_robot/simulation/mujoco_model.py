#!/usr/bin/env python3
"""Generate a MuJoCo model from the canonical spherical-robot parameters.

Generation is not solver execution. The output is a bound input artifact for the
primary multibody evidence layer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = ROOT / "config" / "dimensions.json"
SIMULATION = Path(__file__).resolve().parent / "config.json"


def sha256(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()


def build_xml(
  *,
  ballast_mass_g: float | None = None,
  arm_mm: float | None = None,
  friction_mu: float | None = None,
) -> str:
  dims = json.loads(DIMENSIONS.read_text(encoding="utf-8"))
  sim = json.loads(SIMULATION.read_text(encoding="utf-8"))

  radius = float(dims["sphere_outer_diameter_mm"]) / 2000.0
  wall = float(dims["shell_wall_mm"]) / 1000.0
  selected_ballast_g = float(
    dims["ballast_mass_g"] if ballast_mass_g is None else ballast_mass_g
  )
  ballast = selected_ballast_g / 1000.0
  extra = float(sim["pendulum_extra_mass_g_assumed"]) / 1000.0
  selected_arm_mm = float(
    dims["pendulum_arm_mm"] if arm_mm is None else arm_mm
  )
  arm = selected_arm_mm / 1000.0
  steering_limit = float(dims["steering_limit_deg"])
  selected_friction = float(
    sim["static_friction_mu_values"][1]
    if friction_mu is None
    else friction_mu
  )
  motor_torque = float(dims["tt_motor_torque_nm_PLACEHOLDER"])

  if min(radius, wall, ballast, extra, arm, selected_friction, motor_torque) <= 0:
    raise ValueError("MuJoCo model inputs must be positive")

  shell_volume_cm3 = (
    4.0
    * math.pi
    / 3.0
    * ((radius * 1000.0) ** 3 - ((radius - wall) * 1000.0) ** 3)
    / 1000.0
  )
  shell_mass = shell_volume_cm3 * float(dims["petg_density_g_cm3"]) * 1.07 / 1000.0
  fixed_mass = (
    shell_mass
    + float(dims["estimated_structural_print_volume_cm3"])
    * float(dims["petg_density_g_cm3"])
    / 1000.0
    + float(dims["battery_mass_g_PLACEHOLDER"]) / 1000.0
    + float(dims["main_motor_mass_g_PLACEHOLDER"]) / 1000.0
    + float(dims["estimated_fastener_mass_g"]) / 1000.0
    + float(dims["estimated_electronics_mass_g"]) / 1000.0
  )
  inertia_factor = float(sim["body_inertia_factor_nominal"])
  inertia = inertia_factor * fixed_mass * radius**2

  xml = f"""<mujoco model="spherical_robot">
  <compiler angle="degree" coordinate="local"/>
  <option timestep="0.001" gravity="0 0 -9.80665" integrator="implicitfast"/>
  <default>
    <geom condim="6" friction="{selected_friction:.6f} 0.01 0.002"/>
    <joint damping="0.001"/>
  </default>
  <worldbody>
    <geom name="floor" type="plane" size="3 3 0.1" rgba="0.25 0.25 0.25 1"/>
    <body name="sphere" pos="0 0 {radius:.9f}">
      <freejoint name="sphere_free"/>
      <inertial pos="0 0 0" mass="{fixed_mass:.9f}" diaginertia="{inertia:.9f} {inertia:.9f} {inertia:.9f}"/>
      <geom name="shell_contact" type="sphere" size="{radius:.9f}" mass="0" rgba="0.35 0.55 0.8 0.35"/>
      <site name="imu_site" pos="0 0 0" size="0.006"/>
      <body name="steering_frame" pos="0 0 0">
        <joint name="steering_yaw" type="hinge" axis="0 0 1" range="{-steering_limit:.6f} {steering_limit:.6f}" limited="true"/>
        <geom name="steering_proxy" type="cylinder" size="0.095 0.004" mass="0.08" contype="0" conaffinity="0" rgba="0.8 0.6 0.2 0.5"/>
        <body name="pendulum" pos="0 0 0">
          <joint name="pendulum_hinge" type="hinge" axis="0 1 0" limited="false"/>
          <geom name="pendulum_arm" type="capsule" fromto="0 0 0 0 0 -{arm:.9f}" size="0.006" mass="{extra:.9f}" contype="0" conaffinity="0" rgba="0.8 0.25 0.2 1"/>
          <geom name="ballast" type="sphere" pos="0 0 -{arm:.9f}" size="0.02" mass="{ballast:.9f}" contype="0" conaffinity="0" rgba="0.15 0.15 0.15 1"/>
        </body>
      </body>
    </body>
  </worldbody>
  <actuator>
    <motor name="pendulum_motor" joint="pendulum_hinge" gear="1" ctrllimited="true" ctrlrange="{-motor_torque:.9f} {motor_torque:.9f}"/>
    <motor name="steering_motor" joint="steering_yaw" gear="1" ctrllimited="true" ctrlrange="-0.15 0.15"/>
  </actuator>
  <sensor>
    <jointpos name="pendulum_angle" joint="pendulum_hinge"/>
    <jointvel name="pendulum_speed" joint="pendulum_hinge"/>
    <jointpos name="steering_angle" joint="steering_yaw"/>
    <accelerometer name="imu_accel" site="imu_site"/>
    <gyro name="imu_gyro" site="imu_site"/>
  </sensor>
  <custom>
    <text name="dimensions_sha256" data="{sha256(DIMENSIONS)}"/>
    <text name="simulation_config_sha256" data="{sha256(SIMULATION)}"/>
    <text name="scenario_ballast_g" data="{selected_ballast_g:.6f}"/>
    <text name="scenario_arm_mm" data="{selected_arm_mm:.6f}"/>
    <text name="scenario_friction_mu" data="{selected_friction:.6f}"/>
    <text name="evidence_state" data="GENERATED_MODEL_NOT_EXECUTED"/>
  </custom>
</mujoco>
"""
  ElementTree.fromstring(xml)
  return xml


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "--output",
    type=Path,
    default=ROOT / "exports" / "simulation" / "spherical_robot.mjcf.xml",
  )
  args = parser.parse_args()
  xml = build_xml()
  args.output.parent.mkdir(parents=True, exist_ok=True)
  args.output.write_text(xml, encoding="utf-8")
  print(json.dumps({
    "status": "PASS",
    "artifact": str(args.output),
    "evidence_state": "GENERATED_MODEL_NOT_EXECUTED",
    "physical_accepted": False,
  }))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
