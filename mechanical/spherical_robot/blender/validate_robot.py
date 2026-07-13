"""Fail-closed topology and evaluated-mesh collision validation for P0.2.

This module never repairs geometry. It is run by build_robot.py and can also be
run against the saved blend:
  blender --background spherical_robot.blend --python validate_robot.py
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config" / "dimensions.json").read_text())
REPORT_PATH = ROOT / "exports" / "collision_report.json"


@dataclass
class LocalGeometry:
    vertices: list[Vector]
    triangles: list[tuple[int, int, int]]
    samples: list[Vector]


@dataclass
class WorldGeometry:
    name: str
    bvh: BVHTree
    vertices: list[Vector]
    samples: list[Vector]
    minimum: Vector
    maximum: Vector


def descendants_of(obj, ancestor_name: str) -> bool:
    parent = obj.parent
    while parent:
        if parent.name == ancestor_name:
            return True
        parent = parent.parent
    return False


def primary_subsystem(obj) -> str:
    names = {collection.name for collection in obj.users_collection}
    for name in ("01_SHELL", "02_FIXED_FRAME", "03_STEERING", "04_PENDULUM", "05_ELECTRONICS", "06_FASTENERS", "07_GRIP"):
        if name in names:
            return name
    return "OTHER"


def collision_group(obj) -> str | None:
    explicit = obj.get("COLLISION_GROUP")
    if explicit:
        return str(explicit)
    if descendants_of(obj, "PENDULUM_AXIS"):
        return "PENDULUM_DYNAMIC"
    if descendants_of(obj, "STEERING_FRAME"):
        return "STEERING_DYNAMIC"
    subsystem = primary_subsystem(obj)
    if subsystem in {"01_SHELL", "02_FIXED_FRAME", "05_ELECTRONICS", "06_FASTENERS", "07_GRIP"}:
        return "FIXED_OBSTACLE"
    return None


def active_collision_object(obj) -> bool:
    if obj.type not in {"MESH", "CURVE"} or obj.hide_get():
        return False
    if obj.name.startswith(("SHELL_REFERENCE", "SHELL_TOP", "SHELL_BOTTOM", "FLOOR_")):
        return False
    if "BROAD_PHASE" in obj.name or obj.name.startswith(("COLLISION_", "MIN_CLEARANCE")):
        return False
    if obj.name.startswith("BALLAST_") and obj.name != f"BALLAST_{int(CFG['ballast_mass_g'])}G_PLACEHOLDER":
        return False
    if obj.name == "BATTERY_USER_REPORTED_CANDIDATE":
        return False
    return collision_group(obj) is not None


def evaluated_local_geometry(obj, depsgraph, sample_step=2.0) -> LocalGeometry:
    evaluated = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(evaluated, depsgraph=depsgraph)
    mesh.calc_loop_triangles()
    vertices = [vertex.co.copy() for vertex in mesh.vertices]
    triangles = [tuple(loop.vertices) for loop in mesh.loop_triangles]
    samples = list(vertices)
    for triangle in triangles:
        samples.append((vertices[triangle[0]] + vertices[triangle[1]] + vertices[triangle[2]]) / 3.0)
    for edge in mesh.edges:
        a = vertices[edge.vertices[0]]
        b = vertices[edge.vertices[1]]
        length = (b - a).length
        divisions = max(1, int(math.ceil(length / sample_step)))
        for index in range(1, divisions):
            samples.append(a.lerp(b, index / divisions))
    bpy.data.meshes.remove(mesh)
    return LocalGeometry(vertices, triangles, samples)


def world_geometry(obj, local: LocalGeometry) -> WorldGeometry:
    matrix = obj.matrix_world
    vertices = [matrix @ vertex for vertex in local.vertices]
    samples = [matrix @ point for point in local.samples]
    bvh = BVHTree.FromPolygons(vertices, local.triangles, all_triangles=True, epsilon=1e-6)
    minimum = Vector((min(v.x for v in vertices), min(v.y for v in vertices), min(v.z for v in vertices)))
    maximum = Vector((max(v.x for v in vertices), max(v.y for v in vertices), max(v.z for v in vertices)))
    return WorldGeometry(obj.name, bvh, vertices, samples, minimum, maximum)


def aabb_distance(a: WorldGeometry, b: WorldGeometry) -> float:
    squared = 0.0
    for index in range(3):
        if a.maximum[index] < b.minimum[index]:
            gap = b.minimum[index] - a.maximum[index]
        elif b.maximum[index] < a.minimum[index]:
            gap = a.minimum[index] - b.maximum[index]
        else:
            gap = 0.0
        squared += gap * gap
    return math.sqrt(squared)


def grid_keys(minimum: Vector, maximum: Vector, cell_size: float, expand=0.0):
    lower = [math.floor((minimum[index] - expand) / cell_size) for index in range(3)]
    upper = [math.floor((maximum[index] + expand) / cell_size) for index in range(3)]
    for x in range(lower[0], upper[0] + 1):
        for y in range(lower[1], upper[1] + 1):
            for z in range(lower[2], upper[2] + 1):
                yield (x, y, z)


def sampled_mesh_distance(a: WorldGeometry, b: WorldGeometry, stop_below=None):
    overlaps = a.bvh.overlap(b.bvh)
    if overlaps:
        return -0.001, None, True
    best = float("inf")
    best_point = None
    sources = ((a.samples, b.bvh), (b.samples, a.bvh))
    for points, target in sources:
        for point in points:
            result = target.find_nearest(point)
            if result is None:
                continue
            location, _normal, _index, distance = result
            if distance < best:
                best = distance
                best_point = (point + location) * 0.5
                if stop_below is not None and best < stop_below:
                    return best, best_point, False
    return best, best_point, False


def functional_contact(a: str, b: str) -> bool:
    pair = "|".join(sorted((a, b)))
    rules = (
        ("SHAFT", "BEARING_"),
        ("SHAFT", "PENDULUM_ENCODER"),
        ("FLEXIBLE_COUPLING", "MAIN_MOTOR"),
        ("STEERING_GEAR_SECTOR", "STEERING_PINION"),
        ("STEERING_RING", "YAW_BEARING_PAD"),
        ("STEERING_RING", "YAW_RETAINER"),
        ("STEERING_STOP_TAB", "STEERING_STOP_"),
        ("STEERING_ANGLE_MAGNET", "STEERING_ANGLE_SENSOR"),
        ("PENDULUM_ENCODER_MAGNET", "PENDULUM_ENCODER_SENSOR"),
        ("SHAFT_COLLAR", "BEARING_"),
        ("SHAFT_SPACER", "BEARING_"),
    )
    return any((left in a and right in b) or (left in b and right in a) for left, right in rules)


def topology_metrics(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(evaluated, depsgraph=depsgraph)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    non_manifold = sum(1 for edge in bm.edges if not edge.is_manifold)
    loose_edges = sum(1 for edge in bm.edges if not edge.link_faces)
    loose_vertices = sum(1 for vertex in bm.verts if not vertex.link_edges)
    zero_edges = sum(1 for edge in bm.edges if edge.calc_length() <= 1e-6)
    zero_faces = sum(1 for face in bm.faces if face.calc_area() <= 1e-8)
    face_keys = set()
    duplicate_faces = 0
    for face in bm.faces:
        key = tuple(sorted(vertex.index for vertex in face.verts))
        duplicate_faces += int(key in face_keys)
        face_keys.add(key)
    coordinates = set()
    duplicate_vertices = 0
    for vertex in bm.verts:
        key = tuple(round(value, 6) for value in vertex.co)
        duplicate_vertices += int(key in coordinates)
        coordinates.add(key)
    signed_volume = bm.calc_volume(signed=True) if bm.faces else 0.0
    bm.free()
    bpy.data.meshes.remove(mesh)
    valid = (
        non_manifold == 0 and loose_edges == 0 and loose_vertices == 0
        and zero_edges == 0 and zero_faces == 0 and duplicate_faces == 0
        and duplicate_vertices == 0 and signed_volume > 0.01
    )
    return {
        "valid": valid,
        "manifold": non_manifold == 0,
        "watertight": non_manifold == 0,
        "normals_outward": signed_volume > 0.0,
        "non_manifold_edges": non_manifold,
        "loose_edges": loose_edges,
        "loose_vertices": loose_vertices,
        "zero_length_edges": zero_edges,
        "zero_area_faces": zero_faces,
        "duplicate_faces": duplicate_faces,
        "duplicate_vertices": duplicate_vertices,
        "signed_volume_mm3": round(signed_volume, 3),
    }


def validate_scene(root=ROOT, create_marker=True):
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    source_parts = sorted([obj for obj in bpy.data.objects if obj.type == "MESH" and obj.get("EXPORT_PART") and not obj.name.startswith("EXP_")], key=lambda item: item.name)
    topology = {obj.name: topology_metrics(obj, depsgraph) for obj in source_parts}
    topology_ok = all(row["valid"] for row in topology.values())
    if not topology_ok:
        failed = [name for name, row in topology.items() if not row["valid"]]
        report = {"status": "FAIL_TOPOLOGY", "failed_topology": failed, "topology": topology}
        REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")
        raise RuntimeError(f"Topology validation failed without repair: {failed}")

    objects = [obj for obj in bpy.data.objects if active_collision_object(obj)]
    local = {obj.name: evaluated_local_geometry(obj, depsgraph) for obj in objects}
    fixed_objects = [obj for obj in objects if collision_group(obj) in {"FIXED_OBSTACLE", "WIRE_ENVELOPE"}]
    steering_objects = [obj for obj in objects if collision_group(obj).startswith("STEERING_DYNAMIC")]
    pendulum_objects = [obj for obj in objects if collision_group(obj).startswith("PENDULUM_DYNAMIC")]
    fixed_world = {obj.name: world_geometry(obj, local[obj.name]) for obj in fixed_objects}
    fixed_groups = {}
    for obj in fixed_objects:
        subsystem = "WIRE_ENVELOPE" if collision_group(obj) == "WIRE_ENVELOPE" else primary_subsystem(obj)
        fixed_groups.setdefault(subsystem, []).append(obj)
    spatial_cell_mm = 32.0
    fixed_spatial_index = {}
    for obj in fixed_objects:
        geometry = fixed_world[obj.name]
        for key in grid_keys(geometry.minimum, geometry.maximum, spatial_cell_mm, float(CFG["dynamic_clearance_mm"]) + 2.0):
            fixed_spatial_index.setdefault(key, set()).add(obj.name)
    fixed_by_name = {obj.name: obj for obj in fixed_objects}

    required = float(CFG["dynamic_clearance_mm"])
    min_clearance = float("inf")
    minimum_case = None
    intersections = []
    known_intersecting_pairs = set()
    checked_pairs = 0
    candidate_pairs = 0
    aggregate_tests = 0

    def check_pair(obj_a, geom_a, obj_b, geom_b, yaw, pendulum):
        nonlocal min_clearance, minimum_case, checked_pairs, candidate_pairs
        if functional_contact(obj_a.name, obj_b.name):
            return
        pair_key = tuple(sorted((obj_a.name, obj_b.name)))
        if pair_key in known_intersecting_pairs:
            return
        checked_pairs += 1
        lower_bound = aabb_distance(geom_a, geom_b)
        if lower_bound > required + 2.0:
            return
        candidate_pairs += 1
        distance, point, overlap = sampled_mesh_distance(geom_a, geom_b)
        if overlap:
            known_intersecting_pairs.add(pair_key)
            intersections.append({"a": obj_a.name, "b": obj_b.name, "yaw_deg": yaw, "pendulum_deg": pendulum})
        if distance < min_clearance:
            min_clearance = distance
            minimum_case = {
                "a": obj_a.name,
                "b": obj_b.name,
                "yaw_deg": yaw,
                "pendulum_deg": pendulum,
                "point_mm": [round(value, 3) for value in point] if point else None,
            }

    def check_fixed_groups(moving_obj, moving_geom, yaw, pendulum):
        nonlocal aggregate_tests
        threshold = required + 2.0
        candidate_names = set()
        for key in grid_keys(moving_geom.minimum, moving_geom.maximum, spatial_cell_mm):
            aggregate_tests += 1
            candidate_names.update(fixed_spatial_index.get(key, ()))
        for fixed_name in candidate_names:
            fixed_obj = fixed_by_name[fixed_name]
            fixed_geom = fixed_world[fixed_name]
            if aabb_distance(moving_geom, fixed_geom) <= threshold:
                check_pair(moving_obj, moving_geom, fixed_obj, fixed_geom, yaw, pendulum)

    step_deg = int(os.environ.get("SPHERICAL_ROBOT_VALIDATION_STEP_DEG", "5"))
    if step_deg < 1 or step_deg > 15:
        raise RuntimeError("SPHERICAL_ROBOT_VALIDATION_STEP_DEG must be 1..15; final default is 5")
    yaw_limit = int(round(float(CFG["steering_limit_deg"])))
    yaw_values = list(range(-yaw_limit, yaw_limit + 1, step_deg))
    if yaw_values[-1] != yaw_limit:
        yaw_values.append(yaw_limit)
    pendulum_values = list(range(0, 360, step_deg))
    scene["shell_rotation_deg"] = 0.0
    for yaw in yaw_values:
        scene["steering_angle_deg"] = float(yaw)
        scene["pendulum_angle_deg"] = 0.0
        bpy.context.view_layer.update()
        steering_world = {obj.name: world_geometry(obj, local[obj.name]) for obj in steering_objects}
        for steering_obj in steering_objects:
            geom = steering_world[steering_obj.name]
            check_fixed_groups(steering_obj, geom, yaw, 0)
        for pendulum in pendulum_values:
            scene["pendulum_angle_deg"] = float(pendulum)
            bpy.context.view_layer.update()
            pendulum_world = {obj.name: world_geometry(obj, local[obj.name]) for obj in pendulum_objects}
            for pendulum_obj in pendulum_objects:
                geom = pendulum_world[pendulum_obj.name]
                for steering_obj in steering_objects:
                    check_pair(pendulum_obj, geom, steering_obj, steering_world[steering_obj.name], yaw, pendulum)
                check_fixed_groups(pendulum_obj, geom, yaw, pendulum)

    scene["steering_angle_deg"] = 0.0
    scene["pendulum_angle_deg"] = 0.0
    bpy.context.view_layer.update()

    hatch = CFG["service_hatch_opening_mm"]
    battery_options = [CFG["battery_size_mm_CURRENT_MODEL_PLACEHOLDER"], CFG["battery_size_mm_USER_REPORTED_CANDIDATE"]]
    battery_extraction = all(sorted((dims[1], dims[2]))[0] + 2 * CFG["general_fit_clearance_mm"] <= min(hatch) and sorted((dims[1], dims[2]))[1] + 2 * CFG["general_fit_clearance_mm"] <= max(hatch) for dims in battery_options)
    connectivity_objects = [obj for obj in bpy.data.objects if obj.get("ATTACHES_TO")]
    connectivity_metadata_ok = all(all(obj.get(key) for key in ("FASTENER", "LOAD_SURFACES", "INSTALLATION", "REMOVAL", "TOOL_ACCESS", "ANTI_ROTATION", "AXIAL_RETENTION")) for obj in connectivity_objects)
    status = "MESH_PASS_WITH_PLACEHOLDERS" if not intersections and min_clearance >= required and topology_ok else "FAIL"
    report = {
        "status": status,
        "project_revision": CFG["project_revision"],
        "method": "evaluated Blender meshes; BVH triangle overlap; 2 mm edge surface sampling for distance",
        "broad_phase": "object AABB used only to select BVH candidates",
        "yaw_step_deg": step_deg,
        "pendulum_step_deg": step_deg,
        "yaw_positions": len(yaw_values),
        "pendulum_positions": len(pendulum_values),
        "combinations": len(yaw_values) * len(pendulum_values),
        "required_clearance_mm": required,
        "minimum_clearance_mm": round(min_clearance, 3),
        "minimum_case": minimum_case,
        "intersections": intersections[:100],
        "checked_object_pairs": checked_pairs,
        "bvh_candidate_pairs": candidate_pairs,
        "aggregate_broad_phase_tests": aggregate_tests,
        "fixed_bvh_groups": {name: [obj.name for obj in members] for name, members in fixed_groups.items()},
        "spatial_index_cell_mm": spatial_cell_mm,
        "groups": {
            "pendulum": [obj.name for obj in pendulum_objects],
            "steering": [obj.name for obj in steering_objects],
            "fixed_and_wires": [obj.name for obj in fixed_objects],
        },
        "topology": topology,
        "tool_access_metadata": {"checked_objects": len(connectivity_objects), "complete": connectivity_metadata_ok},
        "battery_extraction_through_hatch": battery_extraction,
        "limitations": [
            "purchased-component meshes remain envelopes until measured",
            "distance is dense mesh-surface sampling after exact BVH intersection testing",
            "proof-load, drop, thermal and real cable-flex tests remain physical tests",
        ],
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    scene["collision_status"] = status
    scene["collision_min_clearance_mm"] = round(min_clearance, 3)
    scene["collision_min_case"] = f"{minimum_case['a']} vs {minimum_case['b']} yaw={minimum_case['yaw_deg']} pendulum={minimum_case['pendulum_deg']}" if minimum_case else "none"
    scene["collision_sample_count"] = len(yaw_values) * len(pendulum_values)
    if create_marker and minimum_case and minimum_case["point_mm"]:
        existing = bpy.data.objects.get("COLLISION_MINIMUM_MARKER")
        if existing:
            bpy.data.objects.remove(existing, do_unlink=True)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=3.0, location=minimum_case["point_mm"])
        marker = bpy.context.object
        marker.name = "COLLISION_MINIMUM_MARKER"
        for coll in list(marker.users_collection):
            coll.objects.unlink(marker)
        bpy.data.collections["COLLISION"].objects.link(marker)
    if status == "FAIL":
        raise RuntimeError(f"Mesh collision validation failed: min={min_clearance:.3f} mm intersections={len(intersections)}")
    return report


if __name__ == "__main__":
    result = validate_scene()
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(json.dumps({"status": result["status"], "minimum_clearance_mm": result["minimum_clearance_mm"]}))
