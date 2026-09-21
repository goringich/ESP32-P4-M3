#!/usr/bin/env python3
"""Compare independent MuJoCo and Project Chrono multibody evidence."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
  value = json.loads(path.read_text(encoding="utf-8"))
  if not isinstance(value, dict):
    raise ValueError(f"{path} must contain an object")
  return value


def scenario_key(row: dict[str, Any]) -> tuple[float, float, float]:
  inputs = row["inputs"]
  return (
    float(inputs["ballast_mass_g"]),
    float(inputs["arm_mm"]),
    float(inputs["friction_mu"]),
  )


def sign(value: float, epsilon: float = 1e-6) -> int:
  if value > epsilon:
    return 1
  if value < -epsilon:
    return -1
  return 0


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument("--mujoco", type=Path, required=True)
  parser.add_argument("--chrono", type=Path, required=True)
  parser.add_argument("--output", type=Path, required=True)
  args = parser.parse_args()

  mujoco = load(args.mujoco)
  chrono = load(args.chrono)
  if mujoco.get("evidence_state") != "PRIMARY_MULTIBODY_PASS":
    raise SystemExit("MuJoCo evidence is not PRIMARY_MULTIBODY_PASS")
  if chrono.get("evidence_state") != "INDEPENDENT_DYNAMICS_CROSSCHECK_PASS":
    raise SystemExit("Chrono evidence is not an independent pass")
  if mujoco["source"]["dimensions_sha256"] != chrono["source"]["dimensions_sha256"]:
    raise SystemExit("solver evidence does not bind the same dimensions revision")
  if mujoco["source"]["simulation_config_sha256"] != chrono["source"]["simulation_config_sha256"]:
    raise SystemExit("solver evidence does not bind the same simulation config")

  mj = {scenario_key(row): row for row in mujoco["scenarios"]}
  ch = {scenario_key(row): row for row in chrono["scenarios"]}
  if set(mj) != set(ch):
    raise SystemExit("solver scenario matrices differ")

  comparisons = []
  directional = 0
  compared = 0
  ratios = []
  for key in sorted(mj):
    mj_disp = float(mj[key]["metrics"]["displacement_m"])
    ch_disp = float(ch[key]["metrics"]["displacement_m"])
    mj_sign = sign(mj_disp)
    ch_sign = sign(ch_disp)
    if mj_sign and ch_sign:
      compared += 1
      directional += int(mj_sign == ch_sign)
      ratio = abs(ch_disp) / max(abs(mj_disp), 1e-12)
      ratios.append(ratio)
    else:
      ratio = None
    comparisons.append({
      "ballast_mass_g": key[0],
      "arm_mm": key[1],
      "friction_mu": key[2],
      "mujoco_displacement_m": mj_disp,
      "chrono_displacement_m": ch_disp,
      "direction_agrees": (
        mj_sign == ch_sign
        if mj_sign and ch_sign
        else None
      ),
      "magnitude_ratio_chrono_over_mujoco": ratio,
    })

  direction_fraction = directional / compared if compared else 0.0
  finite_ratios = [value for value in ratios if math.isfinite(value)]
  median_ratio = (
    sorted(finite_ratios)[len(finite_ratios) // 2]
    if finite_ratios
    else float("inf")
  )
  checks = {
    "all_scenarios_compared": len(comparisons) == 27,
    "direction_agreement_at_least_95pct": direction_fraction >= 0.95,
    "median_magnitude_ratio_bounded": 0.05 <= median_ratio <= 20.0,
    "both_symmetry_checks_pass": (
      bool(mujoco["symmetry_check"]["passed"])
      and bool(chrono["symmetry_check"]["passed"])
    ),
    "both_keep_physical_acceptance_false": (
      mujoco.get("physical_accepted") is False
      and chrono.get("physical_accepted") is False
    ),
  }
  passed = all(checks.values())
  payload = {
    "schema_version": "2026-09-21.spherical-robot-multibody-crosscheck.v1",
    "status": "PASS" if passed else "FAIL",
    "evidence_state": (
      "INDEPENDENT_DYNAMICS_CROSSCHECK_PASS"
      if passed
      else "INDEPENDENT_DYNAMICS_CROSSCHECK_FAIL"
    ),
    "design_verdict": "PROVISIONAL",
    "physical_accepted": False,
    "backends": {
      "primary": mujoco["backend"],
      "independent": chrono["backend"],
    },
    "metrics": {
      "scenario_count": len(comparisons),
      "direction_comparisons": compared,
      "direction_agreement_fraction": direction_fraction,
      "median_magnitude_ratio_chrono_over_mujoco": median_ratio,
    },
    "checks": checks,
    "comparisons": comparisons,
    "limitations": [
      "agreement is a bounded engineering cross-check, not identical trajectory matching",
      "both solvers still depend on unresolved canonical placeholder/assumed inputs",
      "structural FEA, HIL and physical validation remain separate evidence gates",
    ],
  }
  args.output.write_text(
    json.dumps(payload, indent=2) + "\n",
    encoding="utf-8",
  )
  nominal_key = (
    300.0,
    60.0,
    0.45,
  )
  nominal_mj = mj.get(nominal_key)
  nominal_ch = ch.get(nominal_key)
  mj_displacements = [
    abs(float(row["metrics"]["displacement_m"]))
    for row in mj.values()
  ]
  ch_displacements = [
    abs(float(row["metrics"]["displacement_m"]))
    for row in ch.values()
  ]
  diagnostics = {
    "mujoco_displacement_abs_range_m": [
      min(mj_displacements),
      max(mj_displacements),
    ],
    "chrono_displacement_abs_range_m": [
      min(ch_displacements),
      max(ch_displacements),
    ],
    "nominal": {
      "mujoco": nominal_mj["metrics"] if nominal_mj else None,
      "chrono": nominal_ch["metrics"] if nominal_ch else None,
    },
  }
  print(json.dumps({
    "status": payload["status"],
    "evidence_state": payload["evidence_state"],
    "direction_agreement_fraction": direction_fraction,
    "median_magnitude_ratio": median_ratio,
    "diagnostics": diagnostics,
    "output": str(args.output),
  }))
  return 0 if passed else 1


if __name__ == "__main__":
  raise SystemExit(main())
