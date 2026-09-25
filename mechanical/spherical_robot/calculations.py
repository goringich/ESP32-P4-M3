#!/usr/bin/env python3
"""Deterministic first-order sizing report for the spherical pendulum robot."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "config" / "dimensions.json"


class SizingError(ValueError):
  pass


def load_config(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
  data = json.loads(path.read_text(encoding="utf-8"))
  if not isinstance(data, dict):
    raise SizingError("dimensions config must be an object")
  return data


def require_number(cfg: dict[str, Any], key: str) -> float:
  value = cfg.get(key)
  if isinstance(value, bool) or not isinstance(value, (int, float)):
    raise SizingError(f"{key} must be numeric")
  return float(value)


def require_vec3(cfg: dict[str, Any], key: str) -> tuple[float, float, float]:
  value = cfg.get(key)
  if not isinstance(value, list) or len(value) != 3:
    raise SizingError(f"{key} must be a three-value list")
  result = tuple(float(item) for item in value)
  if any(item <= 0 for item in result):
    raise SizingError(f"{key} values must be positive")
  return result


def required_diameter_for_component(
  component: tuple[float, float, float],
  *,
  swept_radius_mm: float,
  clearance_mm: float,
  wall_mm: float,
) -> float:
  x, y, z = component
  center_z = swept_radius_mm + clearance_mm + z / 2.0
  corner_r = math.sqrt((x / 2.0) ** 2 + (y / 2.0) ** 2 + (center_z + z / 2.0) ** 2)
  return 2.0 * (corner_r + clearance_mm + wall_mm)


def sizing_report(cfg: dict[str, Any]) -> dict[str, Any]:
  diameter_mm = require_number(cfg, "sphere_outer_diameter_mm")
  outer_radius_mm = diameter_mm / 2.0
  wall_mm = require_number(cfg, "shell_wall_mm")
  inner_radius_mm = outer_radius_mm - wall_mm
  if inner_radius_mm <= 0:
    raise SizingError("shell wall must be smaller than sphere radius")

  clearance_mm = require_number(cfg, "dynamic_clearance_mm")
  arm_mm = require_number(cfg, "pendulum_arm_mm")
  holder_radius_mm = require_number(cfg, "ballast_holder_outer_diameter_mm") / 2.0
  swept_radius_mm = arm_mm + holder_radius_mm

  board_xy = require_vec3(cfg, "esp32_p4_m3_pcb_mm")
  board = (
    board_xy[0],
    board_xy[1],
    board_xy[2]
    + require_number(cfg, "esp32_top_envelope_height_mm_PLACEHOLDER")
    + require_number(cfg, "esp32_bottom_envelope_height_mm_PLACEHOLDER"),
  )
  battery = require_vec3(cfg, "battery_size_mm_CURRENT_MODEL_PLACEHOLDER")
  minimum_diameter_mm = max(
    required_diameter_for_component(
      board,
      swept_radius_mm=swept_radius_mm,
      clearance_mm=clearance_mm,
      wall_mm=wall_mm,
    ),
    required_diameter_for_component(
      battery,
      swept_radius_mm=swept_radius_mm,
      clearance_mm=clearance_mm,
      wall_mm=wall_mm,
    ),
  )

  shell_volume_cm3 = (
    4.0
    * math.pi
    / 3.0
    * (outer_radius_mm**3 - inner_radius_mm**3)
    / 1000.0
  )
  shell_mass_g = (
    shell_volume_cm3
    * require_number(cfg, "petg_density_g_cm3")
    * 1.07
  )
  structure_mass_g = (
    require_number(cfg, "estimated_structural_print_volume_cm3")
    * require_number(cfg, "petg_density_g_cm3")
  )
  ballast_mass_g = require_number(cfg, "ballast_mass_g")
  body_mass_g = (
    shell_mass_g
    + structure_mass_g
    + require_number(cfg, "battery_mass_g_PLACEHOLDER")
    + require_number(cfg, "main_motor_mass_g_PLACEHOLDER")
    + require_number(cfg, "estimated_fastener_mass_g")
    + require_number(cfg, "estimated_electronics_mass_g")
  )
  total_mass_g = body_mass_g + ballast_mass_g
  if total_mass_g <= 0:
    raise SizingError("total mass must be positive")

  ballast_variants = cfg.get("ballast_variants_g")
  if not isinstance(ballast_variants, list) or not ballast_variants:
    raise SizingError("ballast_variants_g must be a non-empty list")
  arm_variants = cfg.get("pendulum_arm_radii_mm")
  if not isinstance(arm_variants, list) or not arm_variants:
    raise SizingError("pendulum_arm_radii_mm must be a non-empty list")

  ballast_kg = ballast_mass_g / 1000.0
  arm_m = arm_mm / 1000.0
  gravity_torque_nm = ballast_kg * 9.80665 * arm_m

  worst_ballast_g = max(float(value) for value in ballast_variants)
  worst_arm_mm = max(float(value) for value in arm_variants)
  design_gravity_torque_nm = (
    worst_ballast_g / 1000.0
    * 9.80665
    * worst_arm_mm / 1000.0
  )
  continuous_torque_nm = (
    design_gravity_torque_nm
    * require_number(cfg, "design_torque_safety_factor")
    / require_number(cfg, "gearbox_efficiency")
  )
  short_torque_nm = continuous_torque_nm * 1.7
  design_total_mass_g = body_mass_g + worst_ballast_g
  com_shift_mm = worst_ballast_g * worst_arm_mm / design_total_mass_g

  shaft_d_m = require_number(cfg, "shaft_diameter_mm") / 1000.0
  span_m = require_number(cfg, "shaft_support_span_mm") / 1000.0
  worst_moving_mass_kg = (worst_ballast_g + 80.0) / 1000.0
  load_n = worst_moving_mass_kg * 9.80665 * 5.0
  bend_moment_nm = load_n * span_m / 4.0
  bend_stress_mpa = 32.0 * bend_moment_nm / (math.pi * shaft_d_m**3) / 1e6
  bearing_radial_design_n = load_n / 2.0

  sphere_radius_m = outer_radius_mm / 1000.0
  traction_force_n = design_gravity_torque_nm / sphere_radius_m
  minimum_idealized_mu = (
    traction_force_n
    / (design_total_mass_g / 1000.0 * 9.80665)
  )
  shell_rpm_at_target = (
    require_number(cfg, "target_shell_speed_m_s")
    / (2.0 * math.pi * sphere_radius_m)
    * 60.0
  )
  radial_reserve_mm = inner_radius_mm - clearance_mm - swept_radius_mm

  dimension_status = cfg.get("dimension_status")
  if not isinstance(dimension_status, dict):
    raise SizingError("dimension_status must be present")
  unresolved = sorted(
    key
    for key, status in dimension_status.items()
    if status in {"PLACEHOLDER", "ASSUMED"}
  )

  return {
    "project_revision": str(cfg.get("project_revision") or "unknown"),
    "evidence_state": "ANALYTIC_ESTIMATE",
    "sphere": {
      "outer_diameter_mm": diameter_mm,
      "inner_radius_mm": inner_radius_mm,
      "wall_mm": wall_mm,
      "minimum_diameter_from_current_envelopes_mm": minimum_diameter_mm,
    },
    "pendulum": {
      "arm_mm": arm_mm,
      "swept_radius_mm": swept_radius_mm,
      "ballast_mass_g": ballast_mass_g,
      "gravity_torque_nm": gravity_torque_nm,
      "design_ballast_mass_g": worst_ballast_g,
      "design_arm_mm": worst_arm_mm,
      "design_gravity_torque_nm": design_gravity_torque_nm,
      "minimum_continuous_drive_torque_nm": continuous_torque_nm,
      "minimum_short_drive_torque_nm": short_torque_nm,
      "torque_basis": "worst_configured_ballast_and_arm_radius",
    },
    "mass": {
      "shell_mass_g_estimate": shell_mass_g,
      "printed_structure_mass_g_estimate": structure_mass_g,
      "body_mass_excluding_ballast_g_estimate": body_mass_g,
      "total_mass_g_estimate": total_mass_g,
      "maximum_com_shift_mm_estimate": com_shift_mm,
    },
    "shaft": {
      "five_x_shock_bending_stress_mpa_estimate": bend_stress_mpa,
      "bearing_radial_design_load_n_each_estimate": bearing_radial_design_n,
    },
    "rolling": {
      "minimum_idealized_floor_mu": minimum_idealized_mu,
      "recommended_screening_mu_with_margin": max(0.35, minimum_idealized_mu * 2.0),
      "target_shell_speed_m_s": require_number(cfg, "target_shell_speed_m_s"),
      "shell_rpm_at_target": shell_rpm_at_target,
    },
    "clearance": {
      "radial_reserve_mm": radial_reserve_mm,
      "required_dynamic_clearance_mm": clearance_mm,
    },
    "actuator_screening": {
      "motor_torque_nm_placeholder": require_number(cfg, "tt_motor_torque_nm_PLACEHOLDER"),
      "motor_speed_rpm_placeholder": require_number(cfg, "tt_motor_speed_rpm_PLACEHOLDER"),
      "target_output_rpm": require_number(cfg, "target_pendulum_output_rpm"),
      "continuous_torque_margin_nm": (
        require_number(cfg, "tt_motor_torque_nm_PLACEHOLDER") - continuous_torque_nm
      ),
      "short_torque_margin_nm": (
        require_number(cfg, "tt_motor_torque_nm_PLACEHOLDER") - short_torque_nm
      ),
      "meets_continuous_torque_screen": (
        require_number(cfg, "tt_motor_torque_nm_PLACEHOLDER") >= continuous_torque_nm
      ),
      "meets_short_torque_screen": (
        require_number(cfg, "tt_motor_torque_nm_PLACEHOLDER") >= short_torque_nm
      ),
    },
    "unresolved_input_status_keys": unresolved,
    "physical_accepted": False,
    "limitations": [
      "component envelopes marked PLACEHOLDER or ASSUMED require measurement or sourced evidence",
      "load and traction equations are reduced-order screening only",
      "multibody contact dynamics, FEA, HIL and physical tests are separate evidence layers",
    ],
  }


def human_report(report: dict[str, Any]) -> str:
  sphere = report["sphere"]
  pendulum = report["pendulum"]
  mass = report["mass"]
  shaft = report["shaft"]
  rolling = report["rolling"]
  clearance = report["clearance"]
  lines = [
    "SPHERICAL ROBOT — COMPACT SIZING REPORT",
    (
      f"sphere: {sphere['outer_diameter_mm']:.1f} mm OD, "
      f"{sphere['wall_mm']:.1f} mm wall, {sphere['inner_radius_mm']:.1f} mm inner radius"
    ),
    (
      "minimum OD from current swept envelope + component envelopes: "
      f"{sphere['minimum_diameter_from_current_envelopes_mm']:.1f} mm"
    ),
    (
      f"pendulum swept radius: {pendulum['swept_radius_mm']:.1f} mm; "
      f"radial reserve: {clearance['radial_reserve_mm']:.1f} mm"
    ),
    (
      f"shell mass estimate: {mass['shell_mass_g_estimate']:.0f} g; "
      f"printed structure: {mass['printed_structure_mass_g_estimate']:.0f} g"
    ),
    (
      f"total mass estimate: {mass['total_mass_g_estimate']/1000.0:.2f} kg; "
      f"max COM shift: {mass['maximum_com_shift_mm_estimate']:.1f} mm"
    ),
    f"nominal gravity torque: {pendulum['gravity_torque_nm']:.3f} N·m",
    (
      "drive screening target (worst configured ballast/radius): "
      f">= {pendulum['minimum_continuous_drive_torque_nm']:.2f} N·m continuous, "
      f">= {pendulum['minimum_short_drive_torque_nm']:.2f} N·m short"
    ),
    (
      "current placeholder actuator: "
      f"{report['actuator_screening']['motor_torque_nm_placeholder']:.2f} N·m, "
      f"{report['actuator_screening']['motor_speed_rpm_placeholder']:.0f} rpm; "
      "continuous torque screen="
      f"{'PASS' if report['actuator_screening']['meets_continuous_torque_screen'] else 'FAIL'}"
    ),
    (
      "8 mm shaft at 5x shock screening: "
      f"{shaft['five_x_shock_bending_stress_mpa_estimate']:.1f} MPa bending; "
      f"bearing radial design load >= {shaft['bearing_radial_design_load_n_each_estimate']:.0f} N each"
    ),
    (
      f"minimum idealized floor friction coefficient: {rolling['minimum_idealized_floor_mu']:.2f} "
      f"(screen >= {rolling['recommended_screening_mu_with_margin']:.2f})"
    ),
    (
      f"shell speed {rolling['target_shell_speed_m_s']:.2f} m/s corresponds to "
      f"{rolling['shell_rpm_at_target']:.1f} rpm"
    ),
    (
      "NOTE: unresolved PLACEHOLDER/ASSUMED inputs: "
      + (", ".join(report["unresolved_input_status_keys"]) or "none")
    ),
  ]
  return "\n".join(lines)


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
  parser.add_argument("--json", action="store_true")
  args = parser.parse_args()

  try:
    report = sizing_report(load_config(args.config))
  except (OSError, json.JSONDecodeError, SizingError, ValueError) as error:
    print(json.dumps({"status": "FAIL", "error": str(error)}, ensure_ascii=False))
    return 2

  if args.json:
    print(json.dumps({"status": "PASS", "report": report}, ensure_ascii=False, indent=2))
  else:
    print(human_report(report))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
