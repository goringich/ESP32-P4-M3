#!/usr/bin/env python3
"""Compact first-order sizing report for the spherical pendulum robot."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / "config" / "dimensions.json").read_text())


def vec3(key: str) -> tuple[float, float, float]:
    return tuple(float(v) for v in CFG[key])


def main() -> None:
    d = float(CFG["sphere_outer_diameter_mm"])
    ro = d / 2.0
    wall = float(CFG["shell_wall_mm"])
    ri = ro - wall
    clearance = float(CFG["dynamic_clearance_mm"])
    arm = float(CFG["pendulum_arm_mm"])
    holder_r = float(CFG["ballast_holder_outer_diameter_mm"]) / 2.0
    swept_r = arm + holder_r

    board = vec3("esp32_p4_m3_size_mm_PLACEHOLDER")
    battery = vec3("battery_size_mm_PLACEHOLDER")

    def required_diameter(component: tuple[float, float, float]) -> float:
        x, y, z = component
        center_z = swept_r + clearance + z / 2.0
        corner_r = math.sqrt((x / 2.0) ** 2 + (y / 2.0) ** 2 + (center_z + z / 2.0) ** 2)
        return 2.0 * (corner_r + clearance + wall)

    minimum_d = max(required_diameter(board), required_diameter(battery))

    shell_vol_cm3 = 4.0 * math.pi / 3.0 * (ro**3 - ri**3) / 1000.0
    shell_mass_g = shell_vol_cm3 * float(CFG["petg_density_g_cm3"]) * 1.07
    structure_mass_g = float(CFG["estimated_structural_print_volume_cm3"]) * float(CFG["petg_density_g_cm3"])
    total_mass_g = (
        shell_mass_g
        + structure_mass_g
        + float(CFG["ballast_mass_g"])
        + float(CFG["battery_mass_g_PLACEHOLDER"])
        + float(CFG["motor_mass_g_PLACEHOLDER"])
        + float(CFG["estimated_fastener_mass_g"])
        + float(CFG["estimated_electronics_mass_g"])
    )

    ballast_kg = float(CFG["ballast_mass_g"]) / 1000.0
    arm_m = arm / 1000.0
    gravity_torque = ballast_kg * 9.80665 * arm_m
    continuous_torque = gravity_torque * float(CFG["design_torque_safety_factor"]) / float(CFG["gearbox_efficiency"])
    short_torque = continuous_torque * 1.7
    com_shift_mm = float(CFG["ballast_mass_g"]) * arm / total_mass_g

    shaft_d = float(CFG["shaft_diameter_mm"]) / 1000.0
    span = float(CFG["shaft_support_span_mm"]) / 1000.0
    worst_moving_mass_kg = (max(float(v) for v in CFG["ballast_variants_g"]) + 80.0) / 1000.0
    load_n = worst_moving_mass_kg * 9.80665 * 5.0
    bend_moment = load_n * span / 4.0
    bend_stress_mpa = 32.0 * bend_moment / (math.pi * shaft_d**3) / 1e6
    bearing_radial_n = load_n / 2.0

    sphere_r_m = ro / 1000.0
    traction_force = gravity_torque / sphere_r_m
    min_mu = traction_force / (total_mass_g / 1000.0 * 9.80665)
    shell_rpm_at_speed = float(CFG["target_shell_speed_m_s"]) / (2.0 * math.pi * sphere_r_m) * 60.0
    free_radial = ri - clearance - swept_r

    print("SPHERICAL ROBOT — COMPACT SIZING REPORT")
    print(f"sphere: {d:.1f} mm OD, {wall:.1f} mm wall, {ri:.1f} mm inner radius")
    print(f"minimum OD from 360° swept envelope + placeholders: {minimum_d:.1f} mm")
    print(f"pendulum swept radius: {swept_r:.1f} mm; radial reserve: {free_radial:.1f} mm")
    print(f"shell mass estimate: {shell_mass_g:.0f} g; printed structure: {structure_mass_g:.0f} g")
    print(f"total mass estimate: {total_mass_g/1000.0:.2f} kg; max COM shift: {com_shift_mm:.1f} mm")
    print(f"gravity torque: {gravity_torque:.3f} N·m")
    print(f"gearbox target: {CFG['target_pendulum_output_rpm']:.0f} rpm, >= {continuous_torque:.2f} N·m continuous, >= {short_torque:.2f} N·m short")
    print(f"8 mm shaft at 5x shock, 400 g ballast + holder: approx {bend_stress_mpa:.1f} MPa bending; bearing radial design load >= {bearing_radial_n:.0f} N each")
    print(f"minimum idealized floor friction coefficient: {min_mu:.2f} (specify >= {max(0.35, min_mu*2):.2f} with margin)")
    print(f"shell speed {CFG['target_shell_speed_m_s']:.2f} m/s corresponds to {shell_rpm_at_speed:.1f} rpm")
    print("NOTE: component envelopes marked PLACEHOLDER must be measured before final fits are released.")


if __name__ == "__main__":
    main()
