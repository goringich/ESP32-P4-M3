#!/usr/bin/env python3
"""Run a fail-closed CalculiX structural screening analysis on PENDULUM_ARM.

The exact tracked STL is tetrahedralized with Gmsh. The resulting solid is
treated as isotropic PETG only for screening. A passing result never claims
release-qualified FDM material behavior or physical acceptance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any


FEA_ROOT = Path(__file__).resolve().parent
ROBOT_ROOT = FEA_ROOT.parent
CONFIG_PATH = FEA_ROOT / "config.json"
DIMENSIONS_PATH = ROBOT_ROOT / "config" / "dimensions.json"
SIMULATION_PATH = ROBOT_ROOT / "simulation" / "config.json"


class FeaError(RuntimeError):
  pass


def sha256(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
  value = json.loads(path.read_text(encoding="utf-8"))
  if not isinstance(value, dict):
    raise FeaError(f"{path} must contain a JSON object")
  return value


def resolve_ccx() -> str:
  direct = shutil.which("ccx")
  if direct:
    return direct
  candidates = sorted(Path("/usr/bin").glob("ccx*"))
  for candidate in candidates:
    if candidate.is_file() and candidate.stat().st_mode & 0o111:
      return str(candidate)
  raise FeaError("CalculiX executable not found")


def load_case_force_n(
  dimensions: dict[str, Any],
  simulation: dict[str, Any],
  config: dict[str, Any],
) -> float:
  ballast_values = dimensions.get("ballast_variants_g")
  if not isinstance(ballast_values, list) or not ballast_values:
    raise FeaError("ballast_variants_g must be a non-empty list")
  ballast_g = max(float(value) for value in ballast_values)
  extra_g = float(simulation["pendulum_extra_mass_g_assumed"])
  shock = float(config["load_case"]["shock_factor_g"])
  share = float(config["load_case"]["load_share_per_arm"])
  if min(ballast_g, extra_g, shock, share) <= 0:
    raise FeaError("FEA load inputs must be positive")
  return (ballast_g + extra_g) / 1000.0 * 9.80665 * shock * share


def _chunk(values: list[int], width: int = 16) -> list[str]:
  return [
    ", ".join(str(value) for value in values[index:index + width])
    for index in range(0, len(values), width)
  ]


def mesh_stl(
  stl_path: Path,
  config: dict[str, Any],
) -> tuple[dict[int, tuple[float, float, float]], list[tuple[int, tuple[int, int, int, int]]], dict[str, Any]]:
  try:
    import gmsh
  except ImportError as error:
    raise FeaError(f"Gmsh Python module unavailable: {error}") from error

  gmsh.initialize()
  try:
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.model.add("pendulum_arm")
    gmsh.merge(str(stl_path))

    mesh_cfg = config["mesh"]
    angle = math.radians(float(mesh_cfg["classification_angle_deg"]))
    gmsh.model.mesh.classifySurfaces(
      angle,
      True,
      True,
      math.pi,
    )
    gmsh.model.mesh.createGeometry()
    surfaces = gmsh.model.getEntities(2)
    if not surfaces:
      raise FeaError("Gmsh produced no classified STL surfaces")

    loop = gmsh.model.geo.addSurfaceLoop([tag for _dim, tag in surfaces])
    gmsh.model.geo.addVolume([loop])
    gmsh.model.geo.synchronize()

    gmsh.option.setNumber("Mesh.MeshSizeMin", float(mesh_cfg["minimum_size_mm"]))
    gmsh.option.setNumber("Mesh.MeshSizeMax", float(mesh_cfg["maximum_size_mm"]))
    gmsh.option.setNumber("Mesh.ElementOrder", 1)
    gmsh.option.setNumber("Mesh.Optimize", 1)
    gmsh.model.mesh.generate(3)

    node_tags, coordinates, _ = gmsh.model.mesh.getNodes()
    nodes: dict[int, tuple[float, float, float]] = {}
    for index, raw_tag in enumerate(node_tags):
      offset = index * 3
      nodes[int(raw_tag)] = (
        float(coordinates[offset]),
        float(coordinates[offset + 1]),
        float(coordinates[offset + 2]),
      )

    tetrahedra: list[tuple[int, tuple[int, int, int, int]]] = []
    element_types, element_tags, element_nodes = gmsh.model.mesh.getElements(3)
    for element_type, tags, connectivity in zip(
      element_types,
      element_tags,
      element_nodes,
    ):
      name, _dim, _order, node_count, _local, _primary = gmsh.model.mesh.getElementProperties(
        element_type
      )
      if int(node_count) != 4 or "tetra" not in name.lower():
        continue
      flat = [int(value) for value in connectivity]
      for index, raw_element_tag in enumerate(tags):
        start = index * 4
        tetrahedra.append(
          (
            int(raw_element_tag),
            (
              flat[start],
              flat[start + 1],
              flat[start + 2],
              flat[start + 3],
            ),
          )
        )

    if not nodes or not tetrahedra:
      raise FeaError("Gmsh produced no supported 4-node tetrahedral volume mesh")

    values = list(nodes.values())
    minimum = [min(point[axis] for point in values) for axis in range(3)]
    maximum = [max(point[axis] for point in values) for axis in range(3)]
    extents = [maximum[axis] - minimum[axis] for axis in range(3)]
    long_axis = max(range(3), key=lambda axis: extents[axis])
    transverse = [axis for axis in range(3) if axis != long_axis]
    weak_axis = min(transverse, key=lambda axis: extents[axis])

    root_band = float(config["load_case"]["root_band_mm"])
    load_band = float(config["load_case"]["loaded_end_band_mm"])
    root_nodes = sorted(
      tag
      for tag, point in nodes.items()
      if point[long_axis] >= maximum[long_axis] - root_band
    )
    load_nodes = sorted(
      tag
      for tag, point in nodes.items()
      if point[long_axis] <= minimum[long_axis] + load_band
    )
    if len(root_nodes) < 8 or len(load_nodes) < 8:
      raise FeaError(
        f"insufficient boundary nodes: root={len(root_nodes)} load={len(load_nodes)}"
      )

    metadata = {
      "gmsh_version": str(gmsh.__version__),
      "node_count": len(nodes),
      "tetrahedra_count": len(tetrahedra),
      "minimum_mm": minimum,
      "maximum_mm": maximum,
      "extents_mm": extents,
      "long_axis": long_axis,
      "weak_bending_axis": weak_axis,
      "root_node_count": len(root_nodes),
      "load_node_count": len(load_nodes),
      "root_nodes": root_nodes,
      "load_nodes": load_nodes,
    }
    return nodes, tetrahedra, metadata
  finally:
    gmsh.finalize()


def write_calculix_input(
  path: Path,
  *,
  nodes: dict[int, tuple[float, float, float]],
  tetrahedra: list[tuple[int, tuple[int, int, int, int]]],
  mesh_metadata: dict[str, Any],
  load_n: float,
  config: dict[str, Any],
) -> None:
  material = config["material"]
  load_nodes = list(mesh_metadata["load_nodes"])
  root_nodes = list(mesh_metadata["root_nodes"])
  weak_axis = int(mesh_metadata["weak_bending_axis"])
  dof = weak_axis + 1
  per_node_load = -load_n / len(load_nodes)

  lines = [
    "*HEADING",
    "Spherical robot PENDULUM_ARM structural FEA screening",
    "*NODE,NSET=NALL",
  ]
  for tag in sorted(nodes):
    x, y, z = nodes[tag]
    lines.append(f"{tag}, {x:.9f}, {y:.9f}, {z:.9f}")

  lines.append("*ELEMENT,TYPE=C3D4,ELSET=EALL")
  for tag, connectivity in tetrahedra:
    lines.append(f"{tag}, {', '.join(str(value) for value in connectivity)}")

  lines.append("*NSET,NSET=ROOT")
  lines.extend(_chunk(root_nodes))
  lines.append("*NSET,NSET=LOAD")
  lines.extend(_chunk(load_nodes))

  lines.extend([
    "*MATERIAL,NAME=PETG_SCREENING",
    "*ELASTIC",
    (
      f"{float(material['elastic_modulus_mpa']):.9f}, "
      f"{float(material['poisson_ratio']):.9f}"
    ),
    "*SOLID SECTION,ELSET=EALL,MATERIAL=PETG_SCREENING",
    "*BOUNDARY",
    "ROOT, 1, 3, 0.0",
    "*STEP",
    "*STATIC",
    "*CLOAD",
  ])
  for tag in load_nodes:
    lines.append(f"{tag}, {dof}, {per_node_load:.12f}")

  lines.extend([
    "*NODE PRINT,NSET=NALL,FREQUENCY=999999",
    "U",
    "*EL PRINT,ELSET=EALL,FREQUENCY=999999",
    "S",
    "*END STEP",
  ])
  path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def von_mises(stress: tuple[float, float, float, float, float, float]) -> float:
  sxx, syy, szz, sxy, sxz, syz = stress
  return math.sqrt(
    0.5
    * (
      (sxx - syy) ** 2
      + (syy - szz) ** 2
      + (szz - sxx) ** 2
    )
    + 3.0 * (sxy**2 + sxz**2 + syz**2)
  )


def parse_calculix_dat(text: str) -> dict[str, Any]:
  maximum_displacement = 0.0
  maximum_von_mises = 0.0
  displacement_rows = 0
  stress_rows = 0
  mode = ""

  for raw_line in text.splitlines():
    line = raw_line.strip()
    lowered = line.lower()
    if lowered.startswith("displacements (vx,vy,vz)"):
      mode = "displacement"
      continue
    if lowered.startswith("stresses (elem, integ.pnt.,sxx,syy,szz,sxy,sxz,syz)"):
      mode = "stress"
      continue
    if not line:
      continue

    tokens = line.split()
    if mode == "displacement":
      if len(tokens) != 4:
        if not re.match(r"^[+-]?\d", line):
          mode = ""
        continue
      try:
        _node = int(tokens[0])
        values = tuple(float(value) for value in tokens[1:4])
      except ValueError:
        continue
      displacement_rows += 1
      maximum_displacement = max(
        maximum_displacement,
        math.sqrt(sum(value * value for value in values)),
      )
      continue

    if mode == "stress":
      if len(tokens) != 8:
        if not re.match(r"^[+-]?\d", line):
          mode = ""
        continue
      try:
        _element = int(tokens[0])
        _integration_point = int(tokens[1])
        values = tuple(float(value) for value in tokens[2:8])
      except ValueError:
        continue
      stress_rows += 1
      maximum_von_mises = max(
        maximum_von_mises,
        von_mises(values),
      )

  if displacement_rows == 0:
    raise FeaError("CalculiX DAT contains no displacement rows")
  if stress_rows == 0:
    raise FeaError("CalculiX DAT contains no stress rows")

  return {
    "maximum_displacement_mm": maximum_displacement,
    "maximum_von_mises_mpa": maximum_von_mises,
    "displacement_rows": displacement_rows,
    "stress_rows": stress_rows,
  }


def run_solver(input_path: Path) -> tuple[dict[str, Any], str]:
  ccx = resolve_ccx()
  job = input_path.stem
  process = subprocess.run(
    [ccx, "-i", job],
    cwd=input_path.parent,
    text=True,
    capture_output=True,
    check=False,
    timeout=180,
  )
  if process.returncode != 0:
    raise FeaError(
      "CalculiX failed: "
      + (process.stderr[-4000:] or process.stdout[-4000:] or f"rc={process.returncode}")
    )
  dat_path = input_path.with_suffix(".dat")
  if not dat_path.exists():
    raise FeaError("CalculiX completed without a DAT result")
  parsed = parse_calculix_dat(dat_path.read_text(encoding="utf-8", errors="replace"))
  version_process = subprocess.run(
    [ccx, "-v"],
    text=True,
    capture_output=True,
    check=False,
    timeout=10,
  )
  version_text = (version_process.stdout + "\n" + version_process.stderr).strip()
  return parsed, version_text[:1000]


def run(output: Path) -> dict[str, Any]:
  config = read_json(CONFIG_PATH)
  dimensions = read_json(DIMENSIONS_PATH)
  simulation = read_json(SIMULATION_PATH)

  source_stl = (FEA_ROOT / str(config["source_stl"])).resolve()
  if not source_stl.exists():
    raise FeaError(f"source STL missing: {source_stl}")

  load_n = load_case_force_n(dimensions, simulation, config)
  nodes, tetrahedra, mesh = mesh_stl(source_stl, config)
  minimum_tetrahedra = int(config["mesh"]["minimum_tetrahedra"])
  if mesh["tetrahedra_count"] < minimum_tetrahedra:
    raise FeaError(
      f"mesh too coarse: {mesh['tetrahedra_count']} < {minimum_tetrahedra}"
    )

  with tempfile.TemporaryDirectory(prefix="spherical-fea-") as temp_name:
    temp = Path(temp_name)
    input_path = temp / "pendulum_arm.inp"
    write_calculix_input(
      input_path,
      nodes=nodes,
      tetrahedra=tetrahedra,
      mesh_metadata=mesh,
      load_n=load_n,
      config=config,
    )
    result, ccx_version = run_solver(input_path)

  material = config["material"]
  stress_ok = (
    float(result["maximum_von_mises_mpa"])
    <= float(material["screening_allowable_von_mises_mpa"])
  )
  displacement_ok = (
    float(result["maximum_displacement_mm"])
    <= float(material["screening_max_displacement_mm"])
  )
  passed = stress_ok and displacement_ok
  policy = config["evidence_policy"]

  payload = {
    "schema_version": "2026-09-21.spherical-robot-structural-fea-result.v1",
    "status": "PASS" if passed else "FAIL",
    "evidence_state": (
      policy["pass_state"]
      if passed
      else policy["fail_state"]
    ),
    "design_verdict": "PROVISIONAL",
    "physical_accepted": False,
    "part": config["part"],
    "source": {
      "stl": str(source_stl.relative_to(ROBOT_ROOT)),
      "stl_sha256": sha256(source_stl),
      "dimensions_sha256": sha256(DIMENSIONS_PATH),
      "simulation_config_sha256": sha256(SIMULATION_PATH),
      "fea_config_sha256": sha256(CONFIG_PATH),
    },
    "solver": {
      "gmsh_version": mesh["gmsh_version"],
      "calculix_version_text": ccx_version,
      "element_type": "C3D4",
    },
    "load_case": {
      "name": config["load_case"]["name"],
      "total_force_per_arm_n": load_n,
      "shock_factor_g": config["load_case"]["shock_factor_g"],
      "load_share_per_arm": config["load_case"]["load_share_per_arm"],
    },
    "mesh": {
      key: value
      for key, value in mesh.items()
      if key not in {"root_nodes", "load_nodes"}
    },
    "result": result,
    "checks": {
      "stress_screening_pass": stress_ok,
      "displacement_screening_pass": displacement_ok,
      "maximum_von_mises_mpa_limit": material["screening_allowable_von_mises_mpa"],
      "maximum_displacement_mm_limit": material["screening_max_displacement_mm"],
    },
    "material": material,
    "limitations": [
      *material["limitations"],
      "the boundary is a conservative fixed-end abstraction of the two-bolt hub interface",
      "the load is a distributed five-g worst-ballast screening load at the opposite arm end",
      "the tracked STL geometry is analyzed as a fully solid continuum; slicer walls/infill are not explicitly meshed",
      "a pass cannot promote to STRUCTURAL_ANALYSIS_PASS until coupon-backed print properties and a release load case are bound",
    ],
  }
  output.parent.mkdir(parents=True, exist_ok=True)
  output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
  return payload


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "--output",
    type=Path,
    default=ROBOT_ROOT / "exports" / "simulation" / "structural_fea_screening.json",
  )
  args = parser.parse_args()
  try:
    payload = run(args.output)
  except (OSError, ValueError, json.JSONDecodeError, FeaError) as error:
    print(json.dumps({
      "status": "STRUCTURAL_FEA_BLOCKED",
      "error": str(error),
      "physical_accepted": False,
    }))
    return 3
  print(json.dumps({
    "status": payload["status"],
    "evidence_state": payload["evidence_state"],
    "part": payload["part"],
    "maximum_von_mises_mpa": payload["result"]["maximum_von_mises_mpa"],
    "maximum_displacement_mm": payload["result"]["maximum_displacement_mm"],
    "tetrahedra_count": payload["mesh"]["tetrahedra_count"],
    "physical_accepted": payload["physical_accepted"],
    "output": str(args.output),
  }))
  return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
  raise SystemExit(main())
