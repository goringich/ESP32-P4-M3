#!/usr/bin/env python3
"""Run MuJoCo, Project Chrono, and cross-solver comparison in one sandbox."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


SIM_ROOT = Path(__file__).resolve().parent


def build_stage_commands(
  work_dir: Path,
  *,
  python_executable: str = sys.executable,
) -> list[tuple[str, list[str], Path]]:
  mujoco_out = work_dir / "mujoco-evidence.json"
  chrono_out = work_dir / "chrono-evidence.json"
  compare_out = work_dir / "multibody-crosscheck.json"
  return [
    (
      "mujoco",
      [
        python_executable,
        str(SIM_ROOT / "run_mujoco.py"),
        "--output",
        str(mujoco_out),
      ],
      mujoco_out,
    ),
    (
      "chrono",
      [
        python_executable,
        str(SIM_ROOT / "run_chrono.py"),
        "--output",
        str(chrono_out),
      ],
      chrono_out,
    ),
    (
      "compare",
      [
        python_executable,
        str(SIM_ROOT / "compare_multibody.py"),
        "--mujoco",
        str(mujoco_out),
        "--chrono",
        str(chrono_out),
        "--output",
        str(compare_out),
      ],
      compare_out,
    ),
  ]


def compact(text: str, limit: int = 3000) -> str:
  value = text.strip()
  return value[-limit:] if len(value) > limit else value


def load_json_if_present(path: Path) -> dict[str, Any] | None:
  if not path.exists():
    return None
  try:
    value = json.loads(path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError):
    return None
  return value if isinstance(value, dict) else None


def blocker_from_stage(
  stage: str,
  returncode: int,
  stdout: str,
  stderr: str,
  evidence: dict[str, Any] | None,
) -> dict[str, Any]:
  backend_status = str((evidence or {}).get("status") or "")
  if returncode == 3 or backend_status.endswith("_BACKEND_BLOCKED"):
    if stage == "mujoco":
      status = "SIMULATION_BACKEND_BLOCKED"
      backend = "mujoco"
    elif stage == "chrono":
      status = "CROSSCHECK_BACKEND_BLOCKED"
      backend = "project-chrono"
    else:
      status = "VERIFICATION_BACKEND_BLOCKED"
      backend = stage
  else:
    status = "MULTIBODY_VERIFICATION_FAILED"
    backend = stage
  return {
    "status": status,
    "failed_stage": stage,
    "backend": backend,
    "returncode": returncode,
    "stage_evidence": evidence,
    "stdout_excerpt": compact(stdout),
    "stderr_excerpt": compact(stderr),
    "physical_accepted": False,
  }


def execute(output: Path) -> tuple[int, dict[str, Any]]:
  with tempfile.TemporaryDirectory(prefix="spherical-multibody-") as tmp:
    work_dir = Path(tmp)
    stage_receipts: list[dict[str, Any]] = []
    final_evidence: dict[str, Any] | None = None

    for stage, command, stage_output in build_stage_commands(work_dir):
      completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
      )
      evidence = load_json_if_present(stage_output)
      stage_receipts.append({
        "stage": stage,
        "returncode": completed.returncode,
        "evidence_state": (evidence or {}).get("evidence_state"),
        "status": (evidence or {}).get("status"),
      })
      if completed.returncode != 0:
        payload = blocker_from_stage(
          stage,
          completed.returncode,
          completed.stdout,
          completed.stderr,
          evidence,
        )
        payload["stages"] = stage_receipts
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
          json.dumps(payload, indent=2) + "\n",
          encoding="utf-8",
        )
        return completed.returncode, payload
      final_evidence = evidence

    if not isinstance(final_evidence, dict):
      payload = {
        "status": "MULTIBODY_VERIFICATION_FAILED",
        "failed_stage": "compare",
        "reason": "final_evidence_missing",
        "stages": stage_receipts,
        "physical_accepted": False,
      }
      output.parent.mkdir(parents=True, exist_ok=True)
      output.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
      )
      return 2, payload

    payload = {
      **final_evidence,
      "entrypoint": {
        "schema_version": "2026-09-24.spherical-multibody-entrypoint.v1",
        "stages": stage_receipts,
        "single_sandbox_lifetime": True,
      },
      "physical_accepted": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
      json.dumps(payload, indent=2) + "\n",
      encoding="utf-8",
    )
    return 0, payload


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "--output",
    type=Path,
    default=(
      SIM_ROOT.parent
      / "exports"
      / "simulation"
      / "multibody-crosscheck.json"
    ),
  )
  args = parser.parse_args()

  returncode, payload = execute(args.output)
  print(json.dumps({
    "status": payload.get("status"),
    "evidence_state": payload.get("evidence_state"),
    "failed_stage": payload.get("failed_stage"),
    "physical_accepted": payload.get("physical_accepted"),
    "output": str(args.output),
  }))
  return returncode


if __name__ == "__main__":
  raise SystemExit(main())
