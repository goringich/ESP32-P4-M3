#!/usr/bin/env python3
"""Fail-closed repository contract checks for humans, CI, and coding agents."""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = ROOT / "mechanical" / "spherical_robot" / "config" / "dimensions.json"
PRINT_MANIFEST = ROOT / "mechanical" / "spherical_robot" / "exports" / "print_manifest.json"
SDKCONFIG_DEFAULTS = ROOT / "sdkconfig.defaults"
DEPENDENCIES_LOCK = ROOT / "dependencies.lock"

FORBIDDEN_EXACT = {
  "sdkconfig",
  "sdkconfig.old",
  "pytest_hello_world.py",
  "3D-model/fiish.blend1",
}
FORBIDDEN_PREFIXES = (
  "build/",
  "managed_components/",
  ".playwright-mcp/",
)
REVISION_FREE_DOCS = (
  ROOT / "mechanical" / "spherical_robot" / "ASSEMBLY.md",
  ROOT / "mechanical" / "spherical_robot" / "PRINTING.md",
  ROOT / "mechanical" / "spherical_robot" / "NEEDS_MEASUREMENT.md",
  ROOT / "mechanical" / "spherical_robot" / "bom.md",
)
ALLOWED_DIMENSION_STATUS = {
  "MEASURED",
  "DATASHEET",
  "CALCULATED",
  "ASSUMED",
  "PLACEHOLDER",
  "SPECIFIED",
  "USER_REPORTED",
  "IDENTIFIED_FROM_TEST",
}


class ContractError(RuntimeError):
  pass


def read_json(path: Path) -> Any:
  return json.loads(path.read_text(encoding="utf-8"))


def git_lines(*args: str) -> list[str]:
  result = subprocess.run(
    ["git", *args],
    cwd=ROOT,
    check=True,
    capture_output=True,
    text=True,
  )
  return [line for line in result.stdout.splitlines() if line]


def tracked_files() -> list[str]:
  return git_lines("ls-files")


def require(condition: bool, message: str) -> None:
  if not condition:
    raise ContractError(message)


def verify_repository_hygiene(files: list[str]) -> None:
  violations = []
  for path in files:
    if path in FORBIDDEN_EXACT:
      violations.append(path)
      continue
    if any(path.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
      violations.append(path)
      continue
    if "/__pycache__/" in f"/{path}" or path.endswith((".pyc", ".pyo", ".blend1")):
      violations.append(path)

  require(
    not violations,
    "generated/stale tracked artifacts: " + ", ".join(sorted(violations)[:30]),
  )

  gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
  for expected in (
    "build/",
    "managed_components/",
    ".playwright-mcp/",
    "**/__pycache__/",
    "*.py[cod]",
    "*.blend1",
    "sdkconfig",
    "sdkconfig.old",
  ):
    require(expected in gitignore, f".gitignore missing {expected!r}")


def verify_dimensions() -> dict[str, Any]:
  cfg = read_json(DIMENSIONS)
  require(isinstance(cfg, dict), "dimensions.json must contain an object")
  require(bool(str(cfg.get("project_revision") or "").strip()), "project_revision is required")

  diameter = float(cfg["sphere_outer_diameter_mm"])
  shell_wall = float(cfg["shell_wall_mm"])
  structural_wall = float(cfg["structural_wall_mm"])
  minimum_wall = float(cfg["minimum_local_wall_mm"])
  clearance = float(cfg["dynamic_clearance_mm"])
  require(diameter > 2.0 * shell_wall > 0.0, "invalid sphere/shell geometry")
  require(structural_wall >= shell_wall, "structural wall must not be thinner than shell wall")
  require(shell_wall >= minimum_wall > 0.0, "invalid minimum local wall")
  require(clearance > 0.0, "dynamic clearance must be positive")

  ballast = [float(value) for value in cfg["ballast_variants_g"]]
  arms = [float(value) for value in cfg["pendulum_arm_radii_mm"]]
  require(ballast == sorted(set(ballast)) and ballast, "ballast variants must be sorted and unique")
  require(arms == sorted(set(arms)) and arms, "pendulum arm radii must be sorted and unique")
  require(min(ballast) > 0.0 and min(arms) > 0.0, "ballast/arm variants must be positive")

  statuses = cfg.get("dimension_status")
  require(isinstance(statuses, dict) and statuses, "dimension_status must be a non-empty object")
  unknown = sorted({
    str(value)
    for value in statuses.values()
    if str(value) not in ALLOWED_DIMENSION_STATUS
  })
  require(not unknown, "unknown dimension status values: " + ", ".join(unknown))

  return cfg


def verify_print_manifest() -> None:
  manifest = read_json(PRINT_MANIFEST)
  require(isinstance(manifest, list) and manifest, "print manifest must be a non-empty list")

  seen_objects: set[str] = set()
  for index, row in enumerate(manifest):
    require(isinstance(row, dict), f"print manifest row {index} must be an object")
    name = str(row.get("object") or "")
    relative = str(row.get("file") or "")
    require(name and name not in seen_objects, f"invalid/duplicate print object: {name!r}")
    seen_objects.add(name)
    require(relative.startswith("stl/"), f"{name}: print file must live under exports/stl")
    require((PRINT_MANIFEST.parent / relative).is_file(), f"{name}: missing {relative}")
    require(int(row.get("quantity", 0)) > 0, f"{name}: quantity must be positive")
    require(int(row.get("walls", 0)) > 0, f"{name}: walls must be positive")
    infill = float(row.get("infill_percent", -1))
    require(0.0 <= infill <= 100.0, f"{name}: invalid infill percent")


def verify_firmware_identity(files: list[str]) -> None:
  production_sources = [
    path
    for path in files
    if (
      path.startswith("main/")
      or path.startswith("components/")
    ) and path.endswith((".c", ".h", ".cpp", ".hpp", "CMakeLists.txt"))
  ]
  offenders = []
  for relative in production_sources:
    text = (ROOT / relative).read_text(encoding="utf-8", errors="replace")
    if "hello_world_p4" in text:
      offenders.append(relative)
  require(not offenders, "legacy firmware identity remains in: " + ", ".join(offenders))


def verify_dependency_contract() -> None:
  lock = DEPENDENCIES_LOCK.read_text(encoding="utf-8")
  require("version: 5.5.2" in lock, "dependencies.lock must remain bound to ESP-IDF 5.5.2")

  stage = git_lines("ls-files", "--stage", "esp-idf")
  require(len(stage) == 1 and stage[0].startswith("160000 "), "esp-idf must remain a gitlink")

  defaults = SDKCONFIG_DEFAULTS.read_text(encoding="utf-8")
  require(
    "# CONFIG_APP_WIFI_CONNECT is not set" in defaults,
    "tracked defaults must not auto-connect to a private STA network",
  )
  secret_pattern = re.compile(
    r'^CONFIG_APP_WIFI_(?:SSID|PASSWORD)(?:_SECONDARY)?="[^"]+"$',
    re.MULTILINE,
  )
  require(
    secret_pattern.search(defaults) is None,
    "tracked sdkconfig.defaults contains STA credentials",
  )


def verify_revision_authority() -> None:
  for path in REVISION_FREE_DOCS:
    text = path.read_text(encoding="utf-8")
    require(
      re.search(r"\bP\d+\.\d+(?:[-\w]+)?\b", text) is None,
      f"{path.relative_to(ROOT)} duplicates project revision; use dimensions.json authority",
    )


def main() -> int:
  try:
    files = tracked_files()
    verify_repository_hygiene(files)
    cfg = verify_dimensions()
    verify_print_manifest()
    verify_firmware_identity(files)
    verify_dependency_contract()
    verify_revision_authority()
  except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError, ContractError) as error:
    print(f"REPOSITORY_CONTRACT_FAIL: {error}", file=sys.stderr)
    return 1

  unresolved = sorted(
    key
    for key, status in cfg["dimension_status"].items()
    if status in {"PLACEHOLDER", "ASSUMED"}
  )
  print(
    "REPOSITORY_CONTRACT_PASS "
    f"revision={cfg['project_revision']} "
    f"tracked_files={len(files)} "
    f"unresolved_physical_inputs={len(unresolved)}"
  )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
