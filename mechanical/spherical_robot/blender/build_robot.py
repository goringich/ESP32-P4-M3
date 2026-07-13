"""Rebuild the complete spherical pendulum robot in an empty Blender scene.

Run with:
  blender --background --factory-startup --python build_robot.py

Blender coordinates are interpreted as millimetres (Metric, scale_length=0.001).
Unknown purchased-component dimensions are deliberately named *_PLACEHOLDER.
"""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CFG = json.loads((ROOT / "config" / "dimensions.json").read_text())
RENDER_DIR = ROOT / "exports" / "renders"
BLEND_PATH = HERE / "spherical_robot.blend"

COLLECTION_NAMES = [
    "00_REFERENCE",
    "01_SHELL",
    "02_FIXED_FRAME",
    "03_STEERING",
    "04_PENDULUM",
    "05_ELECTRONICS",
    "06_FASTENERS",
    "07_GRIP",
    "08_PRINT_JIGS",
    "09_COLLISION_ENVELOPES",
    "10_EXPORT",
]


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(datablocks):
            if item.users == 0:
                datablocks.remove(item)
    for coll in list(bpy.data.collections):
        if coll.name != "Collection":
            bpy.data.collections.remove(coll)
    base = bpy.data.collections.get("Collection")
    if base:
        base.name = COLLECTION_NAMES[0]
    for name in COLLECTION_NAMES[1:]:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)


def collection(name: str) -> bpy.types.Collection:
    return bpy.data.collections[name]


def move_to_collection(obj: bpy.types.Object, name: str) -> None:
    for coll in list(obj.users_collection):
        coll.objects.unlink(obj)
    collection(name).objects.link(obj)


def material(name: str, color: tuple[float, float, float, float], metallic=0.0, roughness=0.45, transmission=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Alpha"].default_value = color[3]
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = transmission
    if hasattr(mat, "surface_render_method") and color[3] < 1.0:
        mat.surface_render_method = "DITHERED"
    return mat


def assign_material(obj: bpy.types.Object, mat) -> None:
    if obj.data and hasattr(obj.data, "materials"):
        obj.data.materials.append(mat)


def apply_bevel(obj: bpy.types.Object, width=1.0, segments=3) -> None:
    if width <= 0:
        return
    mod = obj.modifiers.new("Manufacturing bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"


def print_meta(obj, material_name="PETG", orientation="largest flat face on bed", walls=5, infill=35, supports=False, brim=False, quantity=1):
    obj["EXPORT_PART"] = True
    obj["PRINT_MATERIAL"] = material_name
    obj["PRINT_ORIENTATION"] = orientation
    obj["PRINT_WALLS"] = walls
    obj["PRINT_INFILL"] = infill
    obj["PRINT_SUPPORTS"] = supports
    obj["PRINT_BRIM"] = brim
    obj["PRINT_QUANTITY"] = quantity
    return obj


def empty(name: str, coll: str, parent=None, display="PLAIN_AXES", size=14.0):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = display
    obj.empty_display_size = size
    collection(coll).objects.link(obj)
    obj.parent = parent
    return obj


def box(name, dims, loc, mat, coll, parent=None, bevel=0.8):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_bevel(obj, min(bevel, min(dims) * 0.2), 3)
    assign_material(obj, mat)
    move_to_collection(obj, coll)
    obj.parent = parent
    return obj


def cylinder(name, radius, depth, loc, mat, coll, parent=None, vertices=64, rotation=(0.0, 0.0, 0.0), bevel=0.4):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    if bevel:
        apply_bevel(obj, bevel, 3)
    assign_material(obj, mat)
    move_to_collection(obj, coll)
    obj.parent = parent
    return obj


def orient_local_z(obj: bpy.types.Object, direction: Vector) -> None:
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector(direction).normalized().to_track_quat("Z", "Y")


def tangent_box(name, tangential_dims, radial_depth, direction, radial_center, mat, coll, parent=None, bevel=0.6):
    direction = Vector(direction).normalized()
    obj = box(name, (tangential_dims[0], tangential_dims[1], radial_depth), direction * radial_center, mat, coll, parent, bevel)
    orient_local_z(obj, direction)
    return obj


def boolean_difference(base, cutter, name="Machined feature"):
    bpy.context.view_layer.objects.active = base
    mod = base.modifiers.new(name, "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    for prior in list(base.modifiers):
        if prior != mod:
            bpy.ops.object.modifier_apply(modifier=prior.name)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def ring(name, outer_d, inner_d, height, loc, mat, coll, parent=None, export=False, quantity=1):
    obj = cylinder(name, outer_d / 2.0, height, loc, mat, coll, parent, bevel=0.5)
    cutter = cylinder(name + "_CUTTER", inner_d / 2.0, height + 4.0, loc, mat, coll, vertices=64, bevel=0)
    boolean_difference(obj, cutter, "Ring bore")
    if export:
        print_meta(obj, quantity=quantity, brim=outer_d > 170)
    return obj


def drilled_box(name, dims, loc, holes, mat, coll, parent=None, bevel=0.8):
    obj = box(name, dims, loc, mat, coll, parent, bevel)
    for idx, (offset, diameter, axis) in enumerate(holes):
        center = Vector(loc) + Vector(offset)
        cutter = cylinder(f"{name}_HOLE_{idx:02d}", diameter / 2.0, max(dims) + 8.0, center, mat, coll, vertices=48, bevel=0)
        orient_local_z(cutter, Vector(axis))
        boolean_difference(obj, cutter, f"Hole {idx+1}")
    return obj


def strut_between(name, a, b, diameter, mat, coll, parent=None, export=False, quantity=1):
    a, b = Vector(a), Vector(b)
    obj = cylinder(name, diameter / 2.0, (b - a).length, (a + b) / 2.0, mat, coll, parent, vertices=32, bevel=0.5)
    orient_local_z(obj, b - a)
    if export:
        print_meta(obj, orientation="axis horizontal; add 5 mm brim tabs", walls=6, infill=45, supports=False, brim=True, quantity=quantity)
    return obj


def arc_bar(name, r_outer, r_inner, height, a0_deg, a1_deg, loc_z, mat, coll, parent=None, steps=24, export=False, quantity=1):
    verts = []
    faces = []
    for i in range(steps + 1):
        a = math.radians(a0_deg + (a1_deg - a0_deg) * i / steps)
        for r in (r_inner, r_outer):
            for z in (-height / 2.0, height / 2.0):
                verts.append((r * math.cos(a), r * math.sin(a), loc_z + z))
    for i in range(steps):
        n = i * 4
        m = (i + 1) * 4
        faces.extend([
            (n + 0, m + 0, m + 1, n + 1),
            (n + 2, n + 3, m + 3, m + 2),
            (n + 0, n + 2, m + 2, m + 0),
            (n + 1, m + 1, m + 3, n + 3),
        ])
    faces.extend([(0, 1, 3, 2), (steps * 4, steps * 4 + 2, steps * 4 + 3, steps * 4 + 1)])
    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection(coll).objects.link(obj)
    obj.parent = parent
    assign_material(obj, mat)
    apply_bevel(obj, 0.6, 3)
    if export:
        print_meta(obj, orientation="flat on bed", walls=6, infill=45, supports=False, brim=False, quantity=quantity)
    return obj


def face_vector(axis: str, u: float, v: float) -> Vector:
    mapping = {
        "+X": Vector((1.0, u, v)), "-X": Vector((-1.0, u, v)),
        "+Y": Vector((u, 1.0, v)), "-Y": Vector((u, -1.0, v)),
        "+Z": Vector((u, v, 1.0)), "-Z": Vector((u, v, -1.0)),
    }
    return mapping[axis].normalized()


def cube_sphere_panel(name: str, axis: str, outer_r: float, inner_r: float, grid: int, mat, parent):
    verts = []
    faces = []
    for radius in (outer_r, inner_r):
        for i in range(grid + 1):
            u = -1.0 + 2.0 * i / grid
            for j in range(grid + 1):
                v = -1.0 + 2.0 * j / grid
                verts.append(tuple(face_vector(axis, u, v) * radius))
    layer = (grid + 1) ** 2
    for i in range(grid):
        for j in range(grid):
            a = i * (grid + 1) + j
            b = (i + 1) * (grid + 1) + j
            c = b + 1
            d = a + 1
            faces.append((a, b, c, d))
            faces.append((layer + d, layer + c, layer + b, layer + a))
    boundary = []
    boundary.extend([i * (grid + 1) for i in range(grid + 1)])
    boundary.extend([grid * (grid + 1) + j for j in range(1, grid + 1)])
    boundary.extend([i * (grid + 1) + grid for i in range(grid - 1, -1, -1)])
    boundary.extend([j for j in range(grid - 1, 0, -1)])
    for k, a in enumerate(boundary):
        b = boundary[(k + 1) % len(boundary)]
        faces.append((a, layer + a, layer + b, b))
    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection("01_SHELL").objects.link(obj)
    obj.parent = parent
    assign_material(obj, mat)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    print_meta(
        obj,
        material_name="PETG or PLA prototype",
        orientation="cube-face rim on bed; outer surface upward",
        walls=5,
        infill=18,
        supports=False,
        brim=True,
    )
    obj["PANEL_AXIS"] = axis
    obj["JOINERY"] = "internal keyed seam clips + recessed M3 screws"
    return obj


def radial_hole(base, axis, u, v, outer_r, wall, diameter, counterbore_d, mat):
    direction = face_vector(axis, u, v)
    cutter = cylinder(base.name + "_M3_CUT", diameter / 2.0, wall + 8.0, direction * (outer_r - wall / 2.0), mat, "00_REFERENCE", vertices=48, bevel=0)
    orient_local_z(cutter, direction)
    boolean_difference(base, cutter, "M3 clearance")
    head = cylinder(base.name + "_HEAD_CUT", counterbore_d / 2.0, 2.0, direction * (outer_r - 0.8), mat, "00_REFERENCE", vertices=48, bevel=0)
    orient_local_z(head, direction)
    boolean_difference(base, head, "Flush screw head")


def grip_pocket(base, axis, u, v, outer_r, wall, mat, grip_mat, index, parent):
    direction = face_vector(axis, u, v)
    depth = float(CFG["tpu_pocket_depth_mm"])
    cutter = tangent_box(
        base.name + f"_GRIP_CUT_{index:02d}",
        (float(CFG["tpu_grip_length_mm"]) + 0.6, float(CFG["tpu_grip_width_mm"]) + 0.6),
        depth + 1.0,
        direction,
        outer_r - depth / 2.0,
        mat,
        "00_REFERENCE",
        bevel=1.8,
    )
    boolean_difference(base, cutter, "Replaceable TPU pocket")
    grip = tangent_box(
        f"TPU_GRIP_{index:02d}_{axis.replace('+','POS_').replace('-','NEG_')}",
        (float(CFG["tpu_grip_length_mm"]), float(CFG["tpu_grip_width_mm"])),
        float(CFG["tpu_grip_thickness_mm"]),
        direction,
        outer_r - float(CFG["tpu_grip_thickness_mm"]) / 2.0 - 0.15,
        grip_mat,
        "07_GRIP",
        parent,
        bevel=1.7,
    )
    grip["REPLACEABLE"] = True
    return grip


def make_hemisphere(name, upper, radius, wall, mat, parent):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=radius)
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, "00_REFERENCE")
    assign_material(obj, mat)
    cutter = box(name + "_CUTTER", (radius * 2.4, radius * 2.4, radius), (0, 0, radius / 2.0 if upper else -radius / 2.0), mat, "00_REFERENCE", bevel=0)
    mod = obj.modifiers.new("Hemisphere", "BOOLEAN")
    mod.operation = "INTERSECT"
    mod.solver = "EXACT"
    mod.object = cutter
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    solid = obj.modifiers.new("Shell wall", "SOLIDIFY")
    solid.thickness = wall
    solid.offset = -1.0
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=solid.name)
    obj.parent = parent
    obj.hide_render = True
    obj.hide_set(True)
    return obj


def add_text(name, body, loc, size, color_mat, coll="00_REFERENCE", parent=None):
    curve = bpy.data.curves.new(name + "_CURVE", "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.size = size
    curve.extrude = 0.15
    obj = bpy.data.objects.new(name, curve)
    collection(coll).objects.link(obj)
    obj.location = loc
    obj.parent = parent
    assign_material(obj, color_mat)
    return obj


def make_driver(obj, data_path, expression):
    fcurve = obj.driver_add(data_path)
    drv = fcurve.driver
    drv.type = "SCRIPTED"
    var = drv.variables.new()
    var.name = "p"
    var.type = "SINGLE_PROP"
    var.targets[0].id_type = "SCENE"
    var.targets[0].id = bpy.context.scene
    var.targets[0].data_path = f'["{expression}"]'
    drv.expression = "radians(p)"


def point_aabb_clearance(point: Vector, radius: float, center, dims) -> float:
    center = Vector(center)
    half = Vector(dims) / 2.0
    delta = Vector((max(abs(point[i] - center[i]) - half[i], 0.0) for i in range(3)))
    return delta.length - radius


def collision_sweep(inner_r: float, parent, yellow, red, green):
    clearance_required = float(CFG["dynamic_clearance_mm"])
    arm = float(CFG["pendulum_arm_mm"])
    holder_r = float(CFG["ballast_holder_outer_diameter_mm"]) / 2.0
    fixed_boxes = {
        "ESP32_P4_M3_PLACEHOLDER": ((0, 0, 97), CFG["esp32_p4_m3_size_mm_PLACEHOLDER"]),
        "BATTERY_PLACEHOLDER": ((0, 0, -98), CFG["battery_size_mm_PLACEHOLDER"]),
        "IMU_MPU9250_PLACEHOLDER": ((75, 0, 40), (4, 20, 15)),
        "IMU_MOUNT": ((80, 0, 40), (3, 28, 23)),
        "MOTOR_DRIVER_PLACEHOLDER": ((0, 94, 40), (45, 12, 35)),
    }
    for idx, a in enumerate((25, 55, 125, 155, 205, 235, 305, 335), start=1):
        rad = math.radians(a)
        fixed_boxes[f"CABLE_CLIP_{idx:02d}"] = ((108 * math.cos(rad), 108 * math.sin(rad), 28 if idx % 2 else -28), (12, 5, 8))
    steering_boxes = {
        "MOTOR_GEARBOX_ENCODER_PLACEHOLDER": ((-72, 0, -4), CFG["motor_gearbox_size_mm_PLACEHOLDER"]),
        "SHAFT_SUPPORT_LEFT": ((-50, 0, 0), (12, 44, 52)),
        "SHAFT_SUPPORT_RIGHT": ((50, 0, 0), (12, 44, 52)),
        "PENDULUM_ENCODER_GUARD": ((61, 0, 0), (6, 30, 30)),
    }
    fixed_segments = []
    for upper in (True, False):
        z = 82 if upper else -82
        for angle in (45, 135, 225, 315):
            a = math.radians(angle)
            fixed_segments.append((
                f"FRAME_STRUT_{'TOP' if upper else 'BOTTOM'}_{angle}",
                Vector((106 * math.cos(a), 106 * math.sin(a), 0)),
                Vector((71 * math.cos(a), 71 * math.sin(a), z)),
                4.0,
            ))

    def point_segment_clearance(point, a, b, moving_radius, segment_radius):
        ab = b - a
        t = max(0.0, min(1.0, (point - a).dot(ab) / ab.length_squared))
        return (point - (a + ab * t)).length - moving_radius - segment_radius

    def annulus_clearance(point, r_inner, r_outer, z_center, half_height, moving_radius):
        radial = math.hypot(point.x, point.y)
        radial_gap = r_inner - radial if radial < r_inner else (radial - r_outer if radial > r_outer else 0.0)
        z_gap = max(abs(point.z - z_center) - half_height, 0.0)
        return math.hypot(radial_gap, z_gap) - moving_radius

    def record(value, target, yaw_deg, pend_deg, point):
        nonlocal min_clear, min_record
        if value < min_clear:
            min_clear, min_record = value, (target, yaw_deg, pend_deg, point.copy())
        if value < clearance_required - 0.05:
            collisions.append((target, yaw_deg, pend_deg, value, point.copy()))
    min_clear = 1e9
    min_record = None
    collisions = []
    for yaw_deg in range(-65, 66, 5):
        yaw = math.radians(yaw_deg)
        for pend_deg in range(0, 360, 5):
            p = math.radians(pend_deg)
            local = Vector((0, arm * math.sin(p), -arm * math.cos(p)))
            point = Vector((local.x * math.cos(yaw) - local.y * math.sin(yaw), local.x * math.sin(yaw) + local.y * math.cos(yaw), local.z))
            shell_clear = inner_r - (point.length + holder_r)
            record(shell_clear, "INNER_SHELL", yaw_deg, pend_deg, point)
            for target, (center, dims) in fixed_boxes.items():
                value = point_aabb_clearance(point, holder_r, center, dims)
                record(value, target, yaw_deg, pend_deg, point)
            for target, (center, dims) in steering_boxes.items():
                record(point_aabb_clearance(local, holder_r, center, dims), target, yaw_deg, pend_deg, point)
            record(annulus_clearance(local, 88, 95, 0, 4, holder_r), "STEERING_RING", yaw_deg, pend_deg, point)
            record(annulus_clearance(point, 101, 111, 0, 4, holder_r), "FIXED_FRAME_RING", yaw_deg, pend_deg, point)
            record(annulus_clearance(point, 66, 75, 82, 3, holder_r), "FIXED_FRAME_TOP", yaw_deg, pend_deg, point)
            record(annulus_clearance(point, 66, 75, -82, 3, holder_r), "FIXED_FRAME_BOTTOM", yaw_deg, pend_deg, point)
            for target, a, b, radius in fixed_segments:
                record(point_segment_clearance(point, a, b, holder_r, radius), target, yaw_deg, pend_deg, point)
            for t in (0.2, 0.4, 0.6, 0.8):
                arm_point = point * t
                local_arm = local * t
                for target, (center, dims) in fixed_boxes.items():
                    value = point_aabb_clearance(arm_point, 6.0, center, dims)
                    record(value, target + "/ARM", yaw_deg, pend_deg, arm_point)
                for target, (center, dims) in steering_boxes.items():
                    record(point_aabb_clearance(local_arm, 6.0, center, dims), target + "/ARM", yaw_deg, pend_deg, arm_point)
                record(annulus_clearance(local_arm, 88, 95, 0, 4, 6), "STEERING_RING/ARM", yaw_deg, pend_deg, arm_point)
                record(annulus_clearance(arm_point, 101, 111, 0, 4, 6), "FIXED_FRAME_RING/ARM", yaw_deg, pend_deg, arm_point)
                for target, a, b, radius in fixed_segments:
                    record(point_segment_clearance(arm_point, a, b, 6, radius), target + "/ARM", yaw_deg, pend_deg, arm_point)

    bpy.context.scene["collision_min_clearance_mm"] = round(min_clear, 3)
    bpy.context.scene["collision_status"] = "PASS" if not collisions else "FAIL"
    bpy.context.scene["collision_sample_count"] = 27 * 72
    bpy.context.scene["collision_min_case"] = f"{min_record[0]} yaw={min_record[1]} pendulum={min_record[2]}" if min_record else "none"

    bpy.ops.mesh.primitive_torus_add(
        major_radius=arm,
        minor_radius=holder_r,
        major_segments=96,
        minor_segments=24,
        rotation=(0, math.radians(90), 0),
    )
    swept = bpy.context.object
    swept.name = "PENDULUM_SWEPT_VOLUME"
    move_to_collection(swept, "09_COLLISION_ENVELOPES")
    assign_material(swept, yellow)
    swept.parent = parent
    swept.hide_render = True

    arm_env = cylinder("ARM_SWEPT_VOLUME", arm, 12.0, (0, 0, 0), yellow, "09_COLLISION_ENVELOPES", parent, vertices=96, rotation=(0, math.radians(90), 0), bevel=0)
    arm_env.hide_render = True

    if collisions:
        for idx, item in enumerate(collisions[:12], start=1):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=3.0, location=item[4])
            marker = bpy.context.object
            marker.name = f"COLLISION_{idx:02d}_{item[0]}"
            move_to_collection(marker, "09_COLLISION_ENVELOPES")
            assign_material(marker, red)
            marker.hide_render = True
    else:
        marker = cylinder("MIN_CLEARANCE_PASS", 4.0, 1.5, min_record[3] if min_record else (0, 0, 0), green, "09_COLLISION_ENVELOPES", vertices=32, bevel=0.2)
        marker.hide_render = True
    return swept, arm_env, collisions


def validate_export_meshes() -> dict:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    report = {"objects": {}, "all_manifold": True}
    for obj in sorted(bpy.data.objects, key=lambda o: o.name):
        if obj.type != "MESH" or not obj.get("EXPORT_PART"):
            continue
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        face_keys = set()
        duplicate_faces = 0
        for face in bm.faces:
            key = tuple(sorted(vertex.index for vertex in face.verts))
            if key in face_keys:
                duplicate_faces += 1
            face_keys.add(key)
        non_manifold_edges = [edge for edge in bm.edges if not edge.is_manifold]
        non_manifold = len(non_manifold_edges)
        non_manifold_face_counts = [len(edge.link_faces) for edge in non_manifold_edges]
        volume = abs(bm.calc_volume(signed=True)) if bm.faces else 0.0
        bm.free()
        eval_obj.to_mesh_clear()
        ok = non_manifold == 0 and duplicate_faces == 0 and volume > 0.01
        report["objects"][obj.name] = {"manifold": ok, "non_manifold_edges": non_manifold, "non_manifold_face_counts": non_manifold_face_counts, "duplicate_faces": duplicate_faces, "volume_mm3": round(volume, 2)}
        report["all_manifold"] = report["all_manifold"] and ok
    return report


def finalize_export_meshes() -> None:
    """Bake modifiers and remove coincident vertices/faces before validation/export."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in sorted(bpy.data.objects, key=lambda item: item.name):
        if obj.type != "MESH" or not obj.get("EXPORT_PART"):
            continue
        evaluated = obj.evaluated_get(depsgraph)
        baked = bpy.data.meshes.new_from_object(evaluated, depsgraph=depsgraph)
        obj.modifiers.clear()
        old = obj.data
        obj.data = baked
        if old.users == 0:
            bpy.data.meshes.remove(old)
        bm = bmesh.new()
        bm.from_mesh(baked)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
        bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=0.0001)
        bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method="BEAUTY", ngon_method="BEAUTY")
        bm.verts.ensure_lookup_table()
        seen = set()
        duplicates = []
        for face in bm.faces:
            key = tuple(sorted(vertex.index for vertex in face.verts))
            if key in seen:
                duplicates.append(face)
            else:
                seen.add(key)
        if duplicates:
            bmesh.ops.delete(bm, geom=duplicates, context="FACES")
        for _ in range(3):
            bad_edges = [edge for edge in bm.edges if not edge.is_manifold]
            if not bad_edges:
                break
            bad_faces = list({face for edge in bad_edges for face in edge.link_faces})
            if bad_faces:
                bmesh.ops.delete(bm, geom=bad_faces, context="FACES")
            wire_edges = [edge for edge in bm.edges if not edge.link_faces]
            if wire_edges:
                bmesh.ops.delete(bm, geom=wire_edges, context="EDGES")
            boundary = [edge for edge in bm.edges if edge.is_boundary]
            if boundary:
                filled = bmesh.ops.holes_fill(bm, edges=boundary, sides=0).get("faces", [])
                if filled:
                    bmesh.ops.triangulate(bm, faces=filled, quad_method="BEAUTY", ngon_method="BEAUTY")
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(baked)
        baked.update()
        bm.free()


def look_at(obj, target=(0, 0, 0)):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_scene(path: Path, camera_loc, target=(0, 0, 0), resolution=640):
    cam = bpy.data.objects["CAMERA"]
    cam.location = camera_loc
    look_at(cam, target)
    scene = bpy.context.scene
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def set_collection_render(name, visible):
    for obj in collection(name).all_objects:
        obj.hide_render = not visible


def create_renders(panel_objects, export_objects):
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    for name in COLLECTION_NAMES:
        if name in {"00_REFERENCE", "08_PRINT_JIGS", "09_COLLISION_ENVELOPES", "10_EXPORT"}:
            set_collection_render(name, False)
        else:
            set_collection_render(name, True)

    render_scene(RENDER_DIR / "transparent_assembly.png", (360, -360, 280), (0, 0, 0))
    render_scene(RENDER_DIR / "top_view.png", (0, 0, 520), (0, 0, 0))
    render_scene(RENDER_DIR / "side_view.png", (480, 0, 40), (0, 0, 0))
    render_scene(RENDER_DIR / "shaft_axis_view.png", (430, 0, 0), (0, 0, 0))

    saved = {obj.name: obj.hide_render for obj in panel_objects}
    for obj in panel_objects:
        if obj.get("PANEL_AXIS") in {"+X", "+Y"}:
            obj.hide_render = True
    render_scene(RENDER_DIR / "section_view.png", (360, -360, 220), (0, 0, 0))
    for obj in panel_objects:
        obj.hide_render = saved[obj.name]

    saved_locs = {obj.name: obj.location.copy() for obj in panel_objects}
    for obj in panel_objects:
        axis = obj.get("PANEL_AXIS")
        obj.location += face_vector(axis, 0, 0) * 70.0
    render_scene(RENDER_DIR / "exploded_view.png", (430, -430, 320), (0, 0, 0), 720)
    for obj in panel_objects:
        obj.location = saved_locs[obj.name]

    set_collection_render("09_COLLISION_ENVELOPES", True)
    render_scene(RENDER_DIR / "collision_check.png", (370, -370, 250), (0, 0, 0))
    render_scene(RENDER_DIR / "swept_volume.png", (420, 0, 80), (0, 0, 0))
    set_collection_render("09_COLLISION_ENVELOPES", False)

    for obj in panel_objects:
        if obj.get("PANEL_AXIS") in {"+X", "+Y"}:
            obj.hide_render = True
    render_scene(RENDER_DIR / "pendulum_closeup.png", (250, -250, 130), (0, 0, -15))
    render_scene(RENDER_DIR / "electronics_layout.png", (280, -280, 260), (0, 0, 30))
    render_scene(RENDER_DIR / "equatorial_joint_closeup.png", (285, -285, 25), (0, 0, 0))
    for obj in panel_objects:
        obj.hide_render = saved[obj.name]

    for name in COLLECTION_NAMES:
        set_collection_render(name, False)
    representatives = [
        bpy.data.objects.get("SHELL_SEGMENT_05_POS_Z"),
        bpy.data.objects.get("STEERING_RING"),
        bpy.data.objects.get("PENDULUM_ARM"),
        bpy.data.objects.get("BALLAST_HOLDER"),
        bpy.data.objects.get("PCB_TRAY"),
        bpy.data.objects.get("M3_TEST_COUPON"),
    ]
    representatives = [o for o in representatives if o]
    state = {o.name: (o.location.copy(), o.rotation_euler.copy(), o.hide_render, o.parent) for o in representatives}
    layout = [(-135, 40, 0), (85, 45, 0), (55, -65, 0), (120, -60, 0), (-35, -75, 0), (-115, -75, 0)]
    for obj, loc in zip(representatives, layout):
        obj.hide_render = False
        obj.parent = None
        obj.location = loc
        if obj.name == "SHELL_SEGMENT_05_POS_Z":
            obj.rotation_euler = (0, 0, 0)
        else:
            obj.rotation_euler = (0, 0, 0)
    render_scene(RENDER_DIR / "print_orientation.png", (0, 0, 760), (-35, -10, 0), 720)
    for obj in representatives:
        obj.location, obj.rotation_euler, obj.hide_render, obj.parent = state[obj.name]
    for name in COLLECTION_NAMES:
        set_collection_render(
            name,
            name not in {"00_REFERENCE", "08_PRINT_JIGS", "09_COLLISION_ENVELOPES", "10_EXPORT"},
        )


def build():
    clear_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 0.001
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene["project_revision"] = CFG["project_revision"]
    scene["steering_angle_deg"] = 0.0
    scene["pendulum_angle_deg"] = 0.0
    scene["shell_rotation_deg"] = 0.0
    scene.frame_start = 1
    scene.frame_end = 160

    white = material("MAT_SHELL_TRANSLUCENT", (0.93, 0.96, 1.0, 0.30), roughness=0.28, transmission=0.15)
    white_solid = material("MAT_SHELL_WHITE", (0.95, 0.96, 0.98, 1.0), roughness=0.38)
    grey = material("MAT_FRAME_GREY", (0.28, 0.31, 0.34, 1.0), roughness=0.45)
    dark = material("MAT_STEEL_DARK", (0.08, 0.10, 0.12, 1.0), metallic=0.8, roughness=0.28)
    orange = material("MAT_PENDULUM_ORANGE", (1.0, 0.24, 0.025, 1.0), roughness=0.35)
    green = material("MAT_PCB_GREEN", (0.03, 0.34, 0.10, 1.0), roughness=0.42)
    blue = material("MAT_BATTERY_BLUE", (0.035, 0.18, 0.72, 1.0), roughness=0.38)
    yellow = material("MAT_SWEPT_YELLOW", (1.0, 0.68, 0.02, 0.20), roughness=0.25, transmission=0.1)
    red = material("MAT_COLLISION_RED", (0.9, 0.015, 0.01, 0.85), roughness=0.35)
    cyan = material("MAT_CLEARANCE_PASS", (0.02, 0.8, 0.42, 0.75), roughness=0.35)
    tpu = material("MAT_TPU_BLACK", (0.015, 0.018, 0.02, 1.0), roughness=0.68)
    brass = material("MAT_BRASS", (0.62, 0.33, 0.06, 1.0), metallic=0.75, roughness=0.3)

    sphere_root = empty("SPHERE_ROOT", "00_REFERENCE", display="SPHERE", size=10)
    shell_root = empty("SHELL", "01_SHELL", sphere_root, display="CIRCLE", size=135)
    fixed_root = empty("FIXED_FRAME", "02_FIXED_FRAME", sphere_root, display="CUBE", size=12)
    electronics_root = empty("ELECTRONICS", "05_ELECTRONICS", sphere_root, display="CUBE", size=10)
    steering_root = empty("STEERING_FRAME", "03_STEERING", sphere_root, display="CIRCLE", size=105)
    pendulum_axis = empty("PENDULUM_AXIS", "04_PENDULUM", steering_root, display="ARROWS", size=18)
    # Root rolls about global Y; steering yaws about Z; pendulum spins about local X.
    fcurve = sphere_root.driver_add("rotation_euler", 1)
    var = fcurve.driver.variables.new(); var.name = "p"; var.type = "SINGLE_PROP"; var.targets[0].id_type = "SCENE"; var.targets[0].id = scene; var.targets[0].data_path = '["shell_rotation_deg"]'; fcurve.driver.expression = "radians(p)"
    fcurve = steering_root.driver_add("rotation_euler", 2)
    var = fcurve.driver.variables.new(); var.name = "p"; var.type = "SINGLE_PROP"; var.targets[0].id_type = "SCENE"; var.targets[0].id = scene; var.targets[0].data_path = '["steering_angle_deg"]'; fcurve.driver.expression = "radians(p)"
    fcurve = pendulum_axis.driver_add("rotation_euler", 0)
    var = fcurve.driver.variables.new(); var.name = "p"; var.type = "SINGLE_PROP"; var.targets[0].id_type = "SCENE"; var.targets[0].id = scene; var.targets[0].data_path = '["pendulum_angle_deg"]'; fcurve.driver.expression = "radians(p)"

    for frame, yaw, pend, roll in [(1, -65, 0, 0), (40, 65, 90, 45), (80, -65, 180, 90), (120, 65, 270, 135), (160, 0, 360, 180)]:
        scene.frame_set(frame)
        for key, value in (("steering_angle_deg", yaw), ("pendulum_angle_deg", pend), ("shell_rotation_deg", roll)):
            scene[key] = float(value)
            scene.keyframe_insert(data_path=f'["{key}"]')
    scene.frame_set(1)
    scene["steering_angle_deg"] = 0.0
    scene["pendulum_angle_deg"] = 0.0
    scene["shell_rotation_deg"] = 0.0

    outer_r = float(CFG["sphere_outer_diameter_mm"]) / 2.0
    wall = float(CFG["shell_wall_mm"])
    inner_r = outer_r - wall
    make_hemisphere("SHELL_TOP", True, outer_r, wall, white_solid, shell_root)
    make_hemisphere("SHELL_BOTTOM", False, outer_r, wall, white_solid, shell_root)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=outer_r)
    reference_sphere = bpy.context.object
    reference_sphere.name = "SHELL_REFERENCE_FULL"
    move_to_collection(reference_sphere, "00_REFERENCE")
    assign_material(reference_sphere, white)
    reference_sphere.parent = shell_root
    reference_sphere.hide_render = True
    reference_sphere.hide_set(True)

    axes = ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]
    panel_objects = []
    grip_index = 1
    for idx, axis in enumerate(axes, start=1):
        safe_axis = axis.replace("+", "POS_").replace("-", "NEG_")
        panel = cube_sphere_panel(f"SHELL_SEGMENT_{idx:02d}_{safe_axis}", axis, outer_r, inner_r, int(CFG["shell_panel_grid"]), white, shell_root)
        panel_objects.append(panel)
        for uv in ((-0.48, -0.32), (-0.48, 0.32), (0.48, -0.32), (0.48, 0.32)):
            grip = grip_pocket(panel, axis, uv[0], uv[1], outer_r, wall, grey, tpu, grip_index, shell_root)
            if grip_index == 1:
                print_meta(grip, material_name="TPU 95A", orientation="flat outer face on bed", walls=3, infill=100, supports=False, brim=False, quantity=24)
            grip_index += 1
        for uv in ((-0.72, 0.62), (0.72, -0.62)):
            radial_hole(panel, axis, uv[0], uv[1], outer_r, wall, float(CFG["m3_clearance_mm"]), float(CFG["m3_counterbore_diameter_mm"]), grey)

    plus_x = panel_objects[0]
    hatch_cutter = tangent_box("SERVICE_HATCH_CUTTER", (92, 58), wall + 10, (1, 0, 0), outer_r - wall / 2, grey, "00_REFERENCE", bevel=4)
    boolean_difference(plus_x, hatch_cutter, "Service hatch opening")
    hatch = tangent_box("SERVICE_HATCH", (91.4, 57.4), 2.2, (1, 0, 0), outer_r - 1.7, white_solid, "01_SHELL", shell_root, bevel=3.6)
    print_meta(hatch, orientation="flat inner face on bed", walls=5, infill=30, supports=False, brim=False)
    for y, z in ((-39, -23), (-39, 23), (39, -23), (39, 23)):
        screw = cylinder(f"SERVICE_HATCH_M3_{y}_{z}", 3.0, 3.0, (outer_r - 0.7, y, z), dark, "06_FASTENERS", shell_root, vertices=32, rotation=(0, math.radians(90), 0), bevel=0.2)
        screw["FASTENER"] = "M3 flush head"
    charge = box("CHARGE_CONNECTOR_PLACEHOLDER", (8, 12, 8), (outer_r - 4, -20, 0), dark, "05_ELECTRONICS", electronics_root, bevel=1.0)
    switch = box("MAIN_SWITCH_PLACEHOLDER", (8, 19.2, 13), (outer_r - 4, 20, 0), dark, "05_ELECTRONICS", electronics_root, bevel=1.0)

    # Internal equatorial seam clips and keyed anti-rotation inserts.
    edge_clips = []
    for idx in range(12):
        a = math.radians(idx * 30.0)
        loc = Vector((math.cos(a), math.sin(a), 0)) * (inner_r - 6.0)
        clip = tangent_box(f"EQUATOR_EDGE_CLIP_{idx+1:02d}", (18, 10), 7.0, (math.cos(a), math.sin(a), 0), inner_r - 6.0, grey, "01_SHELL", shell_root, bevel=1.0)
        if idx == 0:
            hole = cylinder("EDGE_CLIP_INSERT_CUT", float(CFG["m3_heat_insert_hole_mm_PLACEHOLDER"]) / 2.0, 12, loc, grey, "00_REFERENCE", vertices=48, bevel=0)
            orient_local_z(hole, Vector((math.cos(a), math.sin(a), 0)))
            boolean_difference(clip, hole, "Heat insert well PLACEHOLDER")
            print_meta(clip, orientation="flat side on bed", walls=6, infill=60, supports=False, brim=False, quantity=12)
        edge_clips.append(clip)
    key = box("SEGMENT_ALIGNMENT_KEY", (12, 6.0, 4.0), (inner_r - 11, 0, 8), grey, "01_SHELL", shell_root, bevel=0.7)
    print_meta(key, orientation="largest flat face on bed", walls=5, infill=80, supports=False, brim=False, quantity=12)
    key["FIT_CLEARANCE_MM"] = float(CFG["general_fit_clearance_mm"])

    # Fixed equatorial frame: four printable quadrants tied to upper/lower hoops.
    fixed_quads = []
    for idx, a0 in enumerate((0, 90, 180, 270), start=1):
        q = arc_bar(f"FIXED_FRAME_RING_QUADRANT_{idx:02d}", 111, 101, 8, a0 + 2, a0 + 88, 0, grey, "02_FIXED_FRAME", fixed_root, export=(idx == 1), quantity=4)
        fixed_quads.append(q)
    top_ring = ring("FIXED_FRAME_TOP", 150, 132, 6, (0, 0, 82), grey, "02_FIXED_FRAME", fixed_root, export=True)
    bottom_ring = ring("FIXED_FRAME_BOTTOM", 150, 132, 6, (0, 0, -82), grey, "02_FIXED_FRAME", fixed_root, export=True)
    for upper in (True, False):
        z = 82 if upper else -82
        for idx, angle in enumerate((45, 135, 225, 315)):
            a = math.radians(angle)
            start = (106 * math.cos(a), 106 * math.sin(a), 0)
            end = (71 * math.cos(a), 71 * math.sin(a), z)
            strut_between(f"FRAME_STRUT_{'TOP' if upper else 'BOTTOM'}_{idx+1:02d}", start, end, 8.0, grey, "02_FIXED_FRAME", fixed_root, export=(upper and idx == 0), quantity=8)

    # Steering ring with a motor service notch, supports and mechanical stops.
    steering_ring = ring("STEERING_RING", 190, 176, 8, (0, 0, 0), orange, "03_STEERING", steering_root, export=False)
    notch = box("STEERING_RING_MOTOR_NOTCH", (70, 62, 18), (-72, 0, 0), grey, "00_REFERENCE", bevel=0)
    boolean_difference(steering_ring, notch, "Motor replacement opening")
    print_meta(steering_ring, orientation="flat on bed", walls=7, infill=45, supports=False, brim=True)
    steering_ring["YAW_RANGE_DEG"] = [-65.0, 65.0]

    left_support = drilled_box("SHAFT_SUPPORT_LEFT", (12, 44, 52), (-50, 0, 0), [((0, 0, 0), 22.0, (1, 0, 0))], orange, "03_STEERING", steering_root, bevel=1.2)
    right_support = drilled_box("SHAFT_SUPPORT_RIGHT", (12, 44, 52), (50, 0, 0), [((0, 0, 0), 22.0, (1, 0, 0))], orange, "03_STEERING", steering_root, bevel=1.2)
    print_meta(left_support, orientation="broad side on bed", walls=7, infill=55, supports=False, brim=False)
    print_meta(right_support, orientation="broad side on bed", walls=7, infill=55, supports=False, brim=False)
    for obj in (left_support, right_support):
        obj["BEARING_SEAT"] = "PLACEHOLDER; release after bearing coupon"

    bearing_size = CFG["bearing_size_mm_PLACEHOLDER"]
    for name, x in (("BEARING_LEFT_PLACEHOLDER", -50), ("BEARING_RIGHT_PLACEHOLDER", 50)):
        bearing = cylinder(name, bearing_size[1] / 2.0, bearing_size[2], (x, 0, 0), dark, "03_STEERING", steering_root, vertices=64, rotation=(0, math.radians(90), 0), bevel=0.3)
        bore = cylinder(name + "_BORE", bearing_size[0] / 2.0, bearing_size[2] + 2, (x, 0, 0), dark, "00_REFERENCE", vertices=48, bevel=0)
        orient_local_z(bore, Vector((1, 0, 0)))
        boolean_difference(bearing, bore, "Bearing bore")

    motor_mount = drilled_box("MOTOR_MOUNT", (58, 48, 6), (-72, 0, -24), [((-20, -17, 0), 3.4, (0, 0, 1)), ((20, -17, 0), 3.4, (0, 0, 1)), ((-20, 17, 0), 3.4, (0, 0, 1)), ((20, 17, 0), 3.4, (0, 0, 1))], orange, "03_STEERING", steering_root, bevel=1.0)
    print_meta(motor_mount, orientation="flat base on bed", walls=6, infill=45, supports=False, brim=False)
    motor_clamp = drilled_box("MOTOR_CLAMP", (44, 8, 40), (-72, 0, 0), [((0, 0, -14), 3.4, (0, 1, 0)), ((0, 0, 14), 3.4, (0, 1, 0))], orange, "03_STEERING", steering_root, bevel=1.2)
    print_meta(motor_clamp, orientation="broad face on bed", walls=6, infill=50, supports=False, brim=False)
    motor = box("MOTOR_GEARBOX_ENCODER_PLACEHOLDER", CFG["motor_gearbox_size_mm_PLACEHOLDER"], (-72, 0, -4), dark, "03_STEERING", steering_root, bevel=2)
    motor["REPLACEABLE"] = True
    motor["REQUIRED_SPEC"] = "30 rpm; >=0.50 N.m continuous; >=0.86 N.m short; encoder; stall current TBD"
    encoder = cylinder("MOTOR_ENCODER_PLACEHOLDER", 16, 12, (-94, 0, -4), green, "03_STEERING", steering_root, vertices=48, rotation=(0, math.radians(90), 0), bevel=0.6)
    encoder_guard = cylinder("ENCODER_GUARD", 19, 16, (-96, 0, -4), orange, "03_STEERING", steering_root, vertices=48, rotation=(0, math.radians(90), 0), bevel=0.8)
    guard_cut = cylinder("ENCODER_GUARD_CUT", 16.5, 18, (-96, 0, -4), orange, "00_REFERENCE", vertices=48, bevel=0)
    orient_local_z(guard_cut, Vector((1, 0, 0)))
    boolean_difference(encoder_guard, guard_cut, "Encoder cavity")
    print_meta(encoder_guard, orientation="open side upward", walls=5, infill=35, supports=False, brim=False)

    yaw_mount = drilled_box("STEERING_ACTUATOR_MOUNT", (52, 34, 6), (0, -105, 3), [((-18, 0, 0), 3.4, (0, 0, 1)), ((18, 0, 0), 3.4, (0, 0, 1))], grey, "02_FIXED_FRAME", fixed_root, bevel=1.0)
    print_meta(yaw_mount, orientation="flat base on bed", walls=6, infill=45, supports=False, brim=False)
    yaw_actuator = box("STEERING_ACTUATOR_PLACEHOLDER", (40, 22, 40), (0, -105, 24), dark, "02_FIXED_FRAME", fixed_root, bevel=2)
    for side, angle in (("MIN", -65), ("MAX", 65)):
        a = math.radians(angle - 90)
        stop = box(f"STEERING_STOP_{side}", (10, 8, 14), (102 * math.cos(a), 102 * math.sin(a), 0), grey, "02_FIXED_FRAME", fixed_root, bevel=1.0)
        stop.rotation_euler.z = a
    steering_tab = box("STEERING_STOP_TAB", (12, 8, 16), (0, -98, 0), orange, "03_STEERING", steering_root, bevel=1.0)

    # Shaft, adjustable pendulum arm and three physical steel ballast variants.
    shaft = cylinder("SHAFT", float(CFG["shaft_diameter_mm"]) / 2.0, float(CFG["shaft_length_mm"]), (0, 0, 0), dark, "04_PENDULUM", pendulum_axis, vertices=64, rotation=(0, math.radians(90), 0), bevel=0.2)
    shaft["MATERIAL"] = "steel"
    hub = cylinder("PENDULUM_HUB", 13, 16, (0, 0, 0), orange, "04_PENDULUM", pendulum_axis, vertices=64, rotation=(0, math.radians(90), 0), bevel=0.8)
    hub_bore = cylinder("PENDULUM_HUB_BORE", float(CFG["shaft_diameter_mm"]) / 2.0 + 0.15, 20, (0, 0, 0), orange, "00_REFERENCE", vertices=48, bevel=0)
    orient_local_z(hub_bore, Vector((1, 0, 0)))
    boolean_difference(hub, hub_bore, "8 mm shaft fit")
    arm_obj = drilled_box("PENDULUM_ARM", (14, 14, 72), (0, 0, -31), [((0, 0, 31), 8.3, (1, 0, 0)), ((0, 0, -21), 3.4, (1, 0, 0)), ((0, 0, -29), 3.4, (1, 0, 0)), ((0, 0, -37), 3.4, (1, 0, 0))], orange, "04_PENDULUM", pendulum_axis, bevel=3.0)
    print_meta(arm_obj, orientation="broad side on bed", walls=8, infill=70, supports=False, brim=True)
    arm_obj["BALLAST_RADII_MM"] = [52.0, 60.0, 68.0]

    holder = cylinder("BALLAST_HOLDER", 23, 45, (0, 0, -60), orange, "04_PENDULUM", pendulum_axis, vertices=64, rotation=(0, math.radians(90), 0), bevel=0.8)
    cavity = cylinder("BALLAST_CAVITY", 20.3, 42.5, (1.5, 0, -60), orange, "00_REFERENCE", vertices=64, bevel=0)
    orient_local_z(cavity, Vector((1, 0, 0)))
    boolean_difference(holder, cavity, "Steel ballast cavity")
    print_meta(holder, orientation="closed end on bed", walls=7, infill=50, supports=False, brim=False)
    lid = cylinder("BALLAST_LID", 23, 3.2, (24.1, 0, -60), orange, "04_PENDULUM", pendulum_axis, vertices=64, rotation=(0, math.radians(90), 0), bevel=0.6)
    print_meta(lid, orientation="flat on bed", walls=5, infill=60, supports=False, brim=False)
    for idx, mass in enumerate(CFG["ballast_variants_g"]):
        length = float(mass) / (float(CFG["steel_density_g_cm3"]) * math.pi * (float(CFG["ballast_diameter_mm"]) / 20.0) ** 2) * 10.0
        ballast = cylinder(f"BALLAST_{int(mass)}G_PLACEHOLDER", float(CFG["ballast_diameter_mm"]) / 2.0, length, (0, 0, -60), dark, "04_PENDULUM", pendulum_axis, vertices=64, rotation=(0, math.radians(90), 0), bevel=0.5)
        ballast["MATERIAL"] = "steel washers/plates/bar; plastic excluded"
        ballast["MASS_G"] = mass
        ballast.hide_render = mass != CFG["ballast_mass_g"]
        ballast.hide_set(mass != CFG["ballast_mass_g"])

    encoder_magnet = cylinder("PENDULUM_ENCODER_MAGNET_PLACEHOLDER", 4.0, 2.0, (56.5, 0, 0), dark, "04_PENDULUM", pendulum_axis, vertices=32, rotation=(0, math.radians(90), 0), bevel=0.2)
    pend_encoder = box("PENDULUM_ENCODER_SENSOR_PLACEHOLDER", (3, 18, 18), (59, 0, 0), green, "03_STEERING", steering_root, bevel=1.0)
    pend_encoder_guard = drilled_box("PENDULUM_ENCODER_GUARD", (6, 30, 30), (61, 0, 0), [((0, 0, 0), 22.0, (1, 0, 0))], orange, "03_STEERING", steering_root, bevel=2.0)
    print_meta(pend_encoder_guard, orientation="broad face on bed", walls=5, infill=40, supports=False, brim=False)

    # Electronics stay fixed to shell; no wiring crosses the continuously rotating pendulum.
    pcb = box("ESP32_P4_M3_PLACEHOLDER", CFG["esp32_p4_m3_size_mm_PLACEHOLDER"], (0, 0, 97), green, "05_ELECTRONICS", electronics_root, bevel=2)
    pcb["SOURCE"] = "envelope inherited from fiish.blend; hole pattern not released"
    pcb_tray = drilled_box("PCB_TRAY", (102, 72, 4), (0, 0, 85), [((-43, -28, 0), 3.4, (0, 0, 1)), ((43, -28, 0), 3.4, (0, 0, 1)), ((-43, 28, 0), 3.4, (0, 0, 1)), ((43, 28, 0), 3.4, (0, 0, 1))], grey, "05_ELECTRONICS", electronics_root, bevel=2)
    window = box("PCB_TRAY_WINDOW", (82, 52, 8), (0, 0, 85), grey, "00_REFERENCE", bevel=2)
    boolean_difference(pcb_tray, window, "Pendulum clearance window")
    print_meta(pcb_tray, orientation="flat on bed", walls=5, infill=35, supports=False, brim=False)

    battery = box("BATTERY_PLACEHOLDER", CFG["battery_size_mm_PLACEHOLDER"], (0, 0, -98), blue, "05_ELECTRONICS", electronics_root, bevel=4)
    battery["REPLACEABLE"] = True
    battery_tray = drilled_box("BATTERY_TRAY", (82, 50, 3.2), (0, 0, -111), [((-34, -18, 0), 3.4, (0, 0, 1)), ((34, -18, 0), 3.4, (0, 0, 1)), ((-34, 18, 0), 3.4, (0, 0, 1)), ((34, 18, 0), 3.4, (0, 0, 1))], grey, "05_ELECTRONICS", electronics_root, bevel=1.8)
    print_meta(battery_tray, orientation="flat base on bed", walls=6, infill=40, supports=False, brim=False)
    for y in (-23, 23):
        rail = box(f"BATTERY_TRAY_RAIL_{y}", (82, 4, 18), (0, y, -103), grey, "05_ELECTRONICS", electronics_root, bevel=1.2)
    for x in (-25, 25):
        strap = box(f"BATTERY_STRAP_GUIDE_{x}", (4, 54, 4), (x, 0, -88), grey, "05_ELECTRONICS", electronics_root, bevel=1.0)

    imu = box("IMU_MPU9250_PLACEHOLDER", (4, 20, 15), (75, 0, 40), green, "05_ELECTRONICS", electronics_root, bevel=1)
    imu["ORIENTATION"] = "vertical YZ plane; 20x15x4 placeholder envelope"
    imu_mount = drilled_box("IMU_MOUNT", (3, 28, 23), (80, 0, 40), [((0, -9, -6), 2.6, (1, 0, 0)), ((0, 9, -6), 2.6, (1, 0, 0)), ((0, -9, 6), 2.6, (1, 0, 0)), ((0, 9, 6), 2.6, (1, 0, 0))], grey, "05_ELECTRONICS", electronics_root, bevel=0.6)
    print_meta(imu_mount, orientation="broad face on bed", walls=5, infill=50, supports=False, brim=False)
    imu_mount["CENTER_OFFSET_MM"] = 85.0

    driver = box("MOTOR_DRIVER_PLACEHOLDER", (45, 12, 35), (0, 94, 40), green, "05_ELECTRONICS", electronics_root, bevel=2)
    driver_tray = drilled_box("DRIVER_TRAY", (53, 4, 43), (0, 86, 40), [((-20, 0, -15), 3.4, (0, 1, 0)), ((20, 0, -15), 3.4, (0, 1, 0)), ((-20, 0, 15), 3.4, (0, 1, 0)), ((20, 0, 15), 3.4, (0, 1, 0))], grey, "05_ELECTRONICS", electronics_root, bevel=1.5)
    print_meta(driver_tray, orientation="broad face on bed", walls=5, infill=35, supports=False, brim=False)
    switch_holder = drilled_box("SWITCH_HOLDER", (18, 28, 6), (inner_r - 10, 12, 0), [((0, -9, 0), 3.4, (1, 0, 0)), ((0, 9, 0), 3.4, (1, 0, 0))], grey, "05_ELECTRONICS", electronics_root, bevel=1.0)
    charge_holder = drilled_box("CHARGE_PORT_HOLDER", (18, 22, 6), (inner_r - 10, -12, 0), [((0, -7, 0), 3.4, (1, 0, 0)), ((0, 7, 0), 3.4, (1, 0, 0))], grey, "05_ELECTRONICS", electronics_root, bevel=1.0)
    print_meta(switch_holder, orientation="flat on bed", walls=5, infill=45, supports=False, brim=False)
    print_meta(charge_holder, orientation="flat on bed", walls=5, infill=45, supports=False, brim=False)
    for idx, a in enumerate((25, 55, 125, 155, 205, 235, 305, 335), start=1):
        rad = math.radians(a)
        clip = box(f"CABLE_CLIP_{idx:02d}", (12, 5, 8), (108 * math.cos(rad), 108 * math.sin(rad), 28 if idx % 2 else -28), grey, "05_ELECTRONICS", electronics_root, bevel=1.2)
        clip.rotation_euler.z = rad
        clip["CABLE_ROUTE"] = "fixed shell side only; outside pendulum swept volume"
        if idx == 1:
            print_meta(clip, orientation="flat on bed", walls=4, infill=60, supports=False, brim=False, quantity=8)

    # Print jigs and fit coupons.
    stand = ring("BALL_STAND", 176, 138, 22, (0, 0, -145), grey, "08_PRINT_JIGS", None, export=True)
    stand["PRINT_ORIENTATION"] = "flat on bed"
    balance_side = drilled_box("BALANCE_STAND_SIDE", (18, 150, 120), (210, 0, 0), [((0, 0, 35), 10, (1, 0, 0))], grey, "08_PRINT_JIGS", None, bevel=5)
    print_meta(balance_side, orientation="broad side on bed", walls=6, infill=25, supports=False, brim=True, quantity=2)
    test_base = drilled_box("PENDULUM_TEST_STAND_BASE", (180, 90, 8), (0, 220, 0), [((-70, -30, 0), 3.4, (0, 0, 1)), ((70, -30, 0), 3.4, (0, 0, 1)), ((-70, 30, 0), 3.4, (0, 0, 1)), ((70, 30, 0), 3.4, (0, 0, 1))], grey, "08_PRINT_JIGS", None, bevel=3)
    print_meta(test_base, orientation="flat on bed", walls=5, infill=25, supports=False, brim=False)
    test_upright = drilled_box("PENDULUM_TEST_STAND_UPRIGHT", (12, 70, 120), (110, 220, 60), [((0, 0, 40), 22.0, (1, 0, 0)), ((0, -25, -45), 3.4, (1, 0, 0)), ((0, 25, -45), 3.4, (1, 0, 0))], grey, "08_PRINT_JIGS", None, bevel=3)
    print_meta(test_upright, orientation="broad side on bed", walls=6, infill=40, supports=False, brim=True, quantity=2)
    alignment = arc_bar("SEGMENT_ALIGNMENT_TEMPLATE", 130, 124, 14, -18, 18, 0, grey, "08_PRINT_JIGS", export=True)
    alignment.location = (-220, 190, 0)

    m3_coupon = drilled_box("M3_TEST_COUPON", (70, 25, 8), (-220, 0, 0), [((-22, 0, 0), 3.2, (0, 0, 1)), ((0, 0, 0), 3.4, (0, 0, 1)), ((22, 0, 0), 3.6, (0, 0, 1))], grey, "08_PRINT_JIGS", None, bevel=2)
    print_meta(m3_coupon, orientation="flat on bed", walls=5, infill=80, supports=False, brim=False)
    bearing_coupon = drilled_box("BEARING_FIT_COUPON", (85, 34, 10), (-220, -50, 0), [((-27, 0, 0), 21.8, (0, 0, 1)), ((0, 0, 0), 22.0, (0, 0, 1)), ((27, 0, 0), 22.2, (0, 0, 1))], grey, "08_PRINT_JIGS", None, bevel=2)
    print_meta(bearing_coupon, orientation="flat on bed", walls=6, infill=80, supports=False, brim=False)
    joint_coupon = arc_bar("SPHERICAL_JOINT_TEST_FRAGMENT", 130, 127.2, 32, -14, 14, 0, white_solid, "08_PRINT_JIGS", export=True)
    joint_coupon.location = (-220, -110, 0)
    insert_template = drilled_box("HEAT_INSERT_TEMPLATE", (90, 28, 10), (-220, -165, 0), [((-30, 0, 0), 3.8, (0, 0, 1)), ((-10, 0, 0), 4.0, (0, 0, 1)), ((10, 0, 0), 4.2, (0, 0, 1)), ((30, 0, 0), 4.4, (0, 0, 1))], grey, "08_PRINT_JIGS", None, bevel=2)
    print_meta(insert_template, orientation="flat on bed", walls=5, infill=80, supports=False, brim=False)

    swept, arm_env, collisions = collision_sweep(inner_r, steering_root, yellow, red, cyan)
    status_text = add_text("COLLISION_STATUS", f"COLLISION CHECK: {'PASS' if not collisions else 'FAIL'}", (0, -150, 150), 10, cyan if not collisions else red, "09_COLLISION_ENVELOPES")
    status_text.hide_render = True

    # Camera, lighting and neutral floor for reproducible engineering views.
    camera_data = bpy.data.cameras.new("CAMERA_DATA")
    camera = bpy.data.objects.new("CAMERA", camera_data)
    collection("00_REFERENCE").objects.link(camera)
    scene.camera = camera
    camera_data.lens = 62
    for name, loc, energy, size in [
        ("KEY_LIGHT", (260, -240, 360), 1500, 180),
        ("FILL_LIGHT", (-300, -160, 160), 900, 150),
        ("RIM_LIGHT", (40, 320, 300), 1200, 130),
    ]:
        data = bpy.data.lights.new(name + "_DATA", "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(name, data)
        collection("00_REFERENCE").objects.link(light)
        light.location = loc
        look_at(light)
    floor = cylinder("FLOOR_REFERENCE", 420, 5, (0, 0, -136), grey, "00_REFERENCE", vertices=96, bevel=1)
    floor.hide_render = False

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    scene.world.color = (0.025, 0.03, 0.04)

    export_objects = [o for o in bpy.data.objects if o.get("EXPORT_PART")]
    finalize_export_meshes()
    report = validate_export_meshes()
    report["collision_status"] = scene["collision_status"]
    report["minimum_dynamic_clearance_mm"] = scene["collision_min_clearance_mm"]
    report["minimum_case"] = scene["collision_min_case"]
    (ROOT / "exports" / "validation_report.json").write_text(json.dumps(report, indent=2) + "\n")
    if not report["all_manifold"]:
        failed = [name for name, row in report["objects"].items() if not row["manifold"]]
        raise RuntimeError(f"Non-manifold export parts: {failed}")
    if collisions:
        raise RuntimeError(f"Dynamic clearance failed in {len(collisions)} samples; see collision markers")

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    create_renders(panel_objects, export_objects)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    spec = importlib.util.spec_from_file_location("export_parts", HERE / "export_parts.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    print(f"BUILD COMPLETE: {BLEND_PATH}")
    print(f"Collision status: {scene['collision_status']}; minimum clearance {scene['collision_min_clearance_mm']} mm")
    print(f"Printable parts: {len(export_objects)}; manifold: {report['all_manifold']}")


if __name__ == "__main__":
    build()
