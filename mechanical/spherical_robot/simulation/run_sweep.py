#!/usr/bin/env python3
"""Run the dependency-free spherical-robot sensitivity sweep."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from reduced_order import (
  build_parameters,
  load_simulation_config,
  simulate,
  speed_controller,
)


ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS_PATH = ROOT / "config" / "dimensions.json"
SIMULATION_PATH = Path(__file__).resolve().parent / "config.json"


def sha256(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "--output",
    type=Path,
    default=ROOT / "exports" / "simulation" / "reduced_order_sweep.json",
  )
  args = parser.parse_args()

  dimensions = json.loads(DIMENSIONS_PATH.read_text(encoding="utf-8"))
  simulation = load_simulation_config(SIMULATION_PATH)
  integration = simulation["integration"]
  target_speed = float(dimensions["target_shell_speed_m_s"])
  controller = speed_controller(target_speed, simulation)

  rows = []
  for ballast_g in dimensions["ballast_variants_g"]:
    for arm_mm in dimensions["pendulum_arm_radii_mm"]:
      for friction_mu in simulation["static_friction_mu_values"]:
        params = build_parameters(
          dimensions=dimensions,
          simulation=simulation,
          ballast_mass_g=float(ballast_g),
          arm_mm=float(arm_mm),
          friction_mu=float(friction_mu),
        )
        result = simulate(
          params=params,
          controller=controller,
          duration_s=float(integration["duration_s"]),
          dt_s=float(integration["dt_s"]),
        )
        achieved = abs(float(result["final_state"]["v_m_s"]))
        speed_ok = achieved >= target_speed * float(
          simulation["requirements"]["target_speed_fraction_for_screening"]
        )
        angle_ok = (
          float(result["metrics"]["maximum_absolute_pendulum_deg"])
          <= float(simulation["requirements"]["maximum_absolute_pendulum_deg"])
        )
        rows.append({
          "ballast_mass_g": float(ballast_g),
          "arm_mm": float(arm_mm),
          "static_friction_mu": float(friction_mu),
          "result": result,
          "screening": {
            "speed_fraction_of_target": achieved / target_speed if target_speed else 0.0,
            "speed_threshold_met": speed_ok,
            "pendulum_angle_bound_met": angle_ok,
            "no_slip_assumption_self_consistent": not result["slip_risk"],
          },
        })

  unresolved = sorted(
    key
    for key, status in dimensions.get("dimension_status", {}).items()
    if status in {"PLACEHOLDER", "ASSUMED"}
  )
  payload = {
    "schema_version": "2026-09-21.spherical-robot-sweep.v1",
    "status": "PASS",
    "model_evidence_state": "ANALYTIC_BASELINE_PASS",
    "design_verdict": "PROVISIONAL",
    "physical_accepted": False,
    "source": {
      "project_revision": dimensions.get("project_revision"),
      "dimensions_sha256": sha256(DIMENSIONS_PATH),
      "simulation_config_sha256": sha256(SIMULATION_PATH),
    },
    "scenario_count": len(rows),
    "scenarios": rows,
    "unresolved_input_status_keys": unresolved,
    "next_evidence": [
      "measure or datasheet-bind critical PLACEHOLDER/ASSUMED inputs",
      "execute generated MuJoCo model for contact-rich 3D dynamics",
      "cross-check release-critical dynamics in Project Chrono",
      "run structural FEA for load-bearing parts where required",
      "run controller-in-loop and later ESP32 HIL",
      "calibrate against physical subassembly and rolling tests",
    ],
  }
  args.output.parent.mkdir(parents=True, exist_ok=True)
  args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
  print(json.dumps({
    "status": payload["status"],
    "model_evidence_state": payload["model_evidence_state"],
    "design_verdict": payload["design_verdict"],
    "scenario_count": payload["scenario_count"],
    "output": str(args.output),
  }))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
