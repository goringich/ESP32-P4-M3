"""Create print-oriented export duplicates, then export STL and assembly GLB."""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config" / "dimensions.json").read_text())
STL_DIR = ROOT / "exports" / "stl"
GLB_DIR = ROOT / "exports" / "glb"


def deselect() -> None:
    bpy.ops.object.select_all(action="DESELECT")


def unique_right_angle_rotations():
    rotations = []
    signatures = set()
    for rx, ry, rz in itertools.product((0, 90, 180, 270), repeat=3):
        matrix = (
            Matrix.Rotation(math.radians(rz), 4, "Z")
            @ Matrix.Rotation(math.radians(ry), 4, "Y")
            @ Matrix.Rotation(math.radians(rx), 4, "X")
        )
        signature = tuple(round(matrix[row][col], 3) for row in range(3) for col in range(3))
        if signature not in signatures:
            signatures.add(signature)
            rotations.append(((rx, ry, rz), matrix))
    return rotations


ROTATIONS = unique_right_angle_rotations()


def panel_rotation(axis: str):
    mapping = {
        "+Z": (0, 0, 0),
        "-Z": (180, 0, 0),
        "+X": (0, -90, 0),
        "-X": (0, 90, 0),
        "+Y": (90, 0, 0),
        "-Y": (-90, 0, 0),
    }
    angles = mapping[axis]
    matrix = (
        Matrix.Rotation(math.radians(angles[2]), 4, "Z")
        @ Matrix.Rotation(math.radians(angles[1]), 4, "Y")
        @ Matrix.Rotation(math.radians(angles[0]), 4, "X")
    )
    return angles, matrix


def extents(vertices, matrix):
    points = [matrix @ vertex for vertex in vertices]
    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return points, minimum, maximum, maximum - minimum


def choose_rotation(source, vertices):
    if source.get("PANEL_AXIS"):
        return panel_rotation(str(source["PANEL_AXIS"]))
    explicit = tuple(float(value) for value in source.get("PRINT_ROTATION_DEG", (0, 0, 0)))
    if any(abs(value) > 1e-6 for value in explicit):
        matrix = (
            Matrix.Rotation(math.radians(explicit[2]), 4, "Z")
            @ Matrix.Rotation(math.radians(explicit[1]), 4, "Y")
            @ Matrix.Rotation(math.radians(explicit[0]), 4, "X")
        )
        return explicit, matrix
    brim = float(CFG["brim_width_mm"]) if source.get("PRINT_BRIM") else 0.0
    allowed_x = float(CFG["printer_bed_x_mm"]) - 2.0 * float(CFG["printer_edge_margin_mm"]) - 2.0 * brim
    allowed_y = float(CFG["printer_bed_y_mm"]) - 2.0 * float(CFG["printer_edge_margin_mm"]) - 2.0 * brim
    candidates = []
    for angles, matrix in ROTATIONS:
        _points, _minimum, _maximum, dims = extents(vertices, matrix)
        if dims.x <= allowed_x + 1e-5 and dims.y <= allowed_y + 1e-5 and dims.z <= float(CFG["printer_bed_z_mm"]) + 1e-5:
            candidates.append((round(dims.z, 5), round(max(dims.x, dims.y), 5), round(dims.x * dims.y, 5), angles, matrix))
    if not candidates:
        raise RuntimeError(f"No print orientation fits build volume for {source.name}")
    _height, _span, _area, angles, matrix = min(candidates, key=lambda row: row[:3])
    return angles, matrix


def topology_metrics(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    non_manifold = sum(1 for edge in bm.edges if not edge.is_manifold)
    loose_edges = sum(1 for edge in bm.edges if not edge.link_faces)
    zero_edges = sum(1 for edge in bm.edges if edge.calc_length() <= 1e-6)
    zero_faces = sum(1 for face in bm.faces if face.calc_area() <= 1e-8)
    seen_faces = set()
    duplicate_faces = 0
    for face in bm.faces:
        key = tuple(sorted(vertex.index for vertex in face.verts))
        duplicate_faces += int(key in seen_faces)
        seen_faces.add(key)
    coordinates = set()
    duplicate_vertices = 0
    for vertex in bm.verts:
        key = tuple(round(value, 6) for value in vertex.co)
        duplicate_vertices += int(key in coordinates)
        coordinates.add(key)
    volume = bm.calc_volume(signed=True) if bm.faces else 0.0
    bm.free()
    valid = non_manifold == loose_edges == zero_edges == zero_faces == duplicate_faces == duplicate_vertices == 0 and volume > 0.01
    return {
        "valid": valid,
        "non_manifold_edges": non_manifold,
        "loose_edges": loose_edges,
        "zero_length_edges": zero_edges,
        "zero_area_faces": zero_faces,
        "duplicate_faces": duplicate_faces,
        "duplicate_vertices": duplicate_vertices,
        "positive_volume": volume > 0.01,
    }


def prepare_export_duplicates():
    export_collection = bpy.data.collections["EXPORT_READY"]
    for obj in list(export_collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    duplicates = []
    sources = sorted(
        [obj for obj in bpy.data.objects if obj.type == "MESH" and obj.get("EXPORT_PART") and not obj.name.startswith("EXP_")],
        key=lambda item: item.name,
    )
    for source in sources:
        evaluated = source.evaluated_get(depsgraph)
        mesh = bpy.data.meshes.new_from_object(evaluated, depsgraph=depsgraph)
        raw_vertices = [vertex.co.copy() for vertex in mesh.vertices]
        angles, rotation = choose_rotation(source, raw_vertices)
        transformed, minimum, maximum, dims = extents(raw_vertices, rotation)
        translation = Vector((-(minimum.x + maximum.x) / 2.0, -(minimum.y + maximum.y) / 2.0, -minimum.z))
        transform = Matrix.Translation(translation) @ rotation
        mesh.transform(transform)
        mesh.update()
        metrics = topology_metrics(mesh)
        if not metrics["valid"]:
            bpy.data.meshes.remove(mesh)
            raise RuntimeError(f"Export duplicate topology failed without repair: {source.name}: {metrics}")
        duplicate = bpy.data.objects.new("EXP_" + source.name, mesh)
        export_collection.objects.link(duplicate)
        duplicate["EXPORT_DUPLICATE"] = True
        duplicate["SOURCE_OBJECT"] = source.name
        duplicate["PRINT_ROTATION_APPLIED_DEG"] = list(angles)
        duplicate["PRINT_STATUS"] = source.get("PRINT_STATUS", "PROTOTYPE_READY")
        duplicate["KNOWN_PLACEHOLDERS"] = source.get("KNOWN_PLACEHOLDERS", "")
        duplicate.hide_render = True
        duplicates.append((source, duplicate, dims, angles, metrics))
    return duplicates


def export_stl(obj: bpy.types.Object, path: Path) -> None:
    deselect()
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(
        filepath=str(path),
        export_selected_objects=True,
        apply_modifiers=True,
        ascii_format=False,
    )


def validate_written_stl(path: Path):
    """Re-import and validate the actual written STL; never modify the source."""
    deselect()
    bpy.ops.wm.stl_import(filepath=str(path), merge_vertices=True)
    imported = list(bpy.context.selected_objects)
    if len(imported) != 1:
        raise RuntimeError(f"Unexpected STL import object count for {path.name}: {len(imported)}")
    obj = imported[0]
    metrics = topology_metrics(obj.data)
    dimensions = tuple(round(value, 3) for value in obj.dimensions)
    minimum_z = min((obj.matrix_world @ Vector(corner)).z for corner in obj.bound_box)
    bpy.data.objects.remove(obj, do_unlink=True)
    if not metrics["valid"]:
        raise RuntimeError(f"Written STL validation failed without repair: {path.name}: {metrics}")
    return metrics, dimensions, minimum_z


def main(prepared=None) -> list[dict]:
    STL_DIR.mkdir(parents=True, exist_ok=True)
    GLB_DIR.mkdir(parents=True, exist_ok=True)
    prepared = prepared or prepare_export_duplicates()
    manifest = []
    expected = set()
    for source, duplicate, _pre_dims, angles, metrics in prepared:
        filename = f"{source.name}.stl"
        expected.add(filename)
        stl_path = STL_DIR / filename
        export_stl(duplicate, stl_path)
        stl_metrics, dims, z_min = validate_written_stl(stl_path)
        brim = float(CFG["brim_width_mm"]) if source.get("PRINT_BRIM") else 0.0
        build_ok = (
            dims[0] + 2 * brim <= float(CFG["printer_bed_x_mm"]) - 2 * float(CFG["printer_edge_margin_mm"]) + 1e-5
            and dims[1] + 2 * brim <= float(CFG["printer_bed_y_mm"]) - 2 * float(CFG["printer_edge_margin_mm"]) + 1e-5
            and dims[2] <= float(CFG["printer_bed_z_mm"]) + 1e-5
            and abs(z_min) < 1e-4
        )
        if not build_ok:
            raise RuntimeError(f"Print-oriented STL does not fit or touch Z=0: {source.name} dims={dims}")
        manifest.append({
            "source_object": source.name,
            "export_object": duplicate.name,
            "stl": f"stl/{filename}",
            "material": source.get("PRINT_MATERIAL", "PETG"),
            "orientation": source.get("PRINT_ORIENTATION", "largest stable face"),
            "rotation_applied_deg": list(angles),
            "dimensions_mm": list(dims),
            "z_min_mm": 0.0,
            "quantity": source.get("PRINT_QUANTITY", 1),
            "walls": source.get("PRINT_WALLS", 5),
            "infill_percent": source.get("PRINT_INFILL", 35),
            "supports": bool(source.get("PRINT_SUPPORTS", False)),
            "brim": bool(source.get("PRINT_BRIM", False)),
            "status": source.get("PRINT_STATUS", "PROTOTYPE_READY"),
            "known_placeholders": source.get("KNOWN_PLACEHOLDERS", ""),
            "applied_scale": [1.0, 1.0, 1.0],
            "build_volume_ok": build_ok,
            "mesh_validation": metrics,
            "written_stl_validation": stl_metrics,
        })
    for stale in STL_DIR.glob("*.stl"):
        if stale.name not in expected:
            stale.unlink()

    assembly_collections = {"01_SHELL", "02_FIXED_FRAME", "03_STEERING", "04_PENDULUM", "05_ELECTRONICS", "06_FASTENERS", "07_GRIP"}
    deselect()
    for obj in bpy.data.objects:
        if not obj.name.startswith("EXP_") and any(collection.name in assembly_collections for collection in obj.users_collection):
            obj.hide_set(False)
            obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_DIR / "spherical_robot_assembly.glb"),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
    )
    (ROOT / "exports" / "print_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print_ready = sum(1 for row in manifest if row["status"] == "PRINT_READY")
    print(f"Exported {len(manifest)} print-oriented STL files ({print_ready} PRINT_READY) and assembly GLB")
    return manifest


if __name__ == "__main__":
    main()
