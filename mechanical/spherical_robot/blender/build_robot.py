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
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector


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
    "EDITABLE",
    "EXPORT_READY",
    "REFERENCE",
    "PLACEHOLDERS",
    "COLLISION",
    "FASTENERS",
]
PRIMARY_COLLECTIONS = COLLECTION_NAMES[:11]


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


def link_to_collection(obj: bpy.types.Object, name: str) -> None:
    coll = collection(name)
    if obj.name not in coll.objects:
        coll.objects.link(obj)


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


def print_meta(
    obj,
    material_name="PETG",
    orientation="largest flat face on bed",
    walls=5,
    infill=35,
    supports=False,
    brim=False,
    quantity=1,
    status="PROTOTYPE_READY",
    print_rotation_deg=(0.0, 0.0, 0.0),
    placeholders="",
):
    obj["EXPORT_PART"] = True
    obj["PRINT_MATERIAL"] = material_name
    obj["PRINT_ORIENTATION"] = orientation
    obj["PRINT_WALLS"] = walls
    obj["PRINT_INFILL"] = infill
    obj["PRINT_SUPPORTS"] = supports
    obj["PRINT_BRIM"] = brim
    obj["PRINT_QUANTITY"] = quantity
    obj["PRINT_STATUS"] = status
    obj["PRINT_ROTATION_DEG"] = list(print_rotation_deg)
    obj["KNOWN_PLACEHOLDERS"] = placeholders
    link_to_collection(obj, "EDITABLE")
    return obj


def mechanical_connection(
    obj,
    attaches_to,
    fastener,
    load_surfaces,
    install,
    removal,
    tool,
    anti_rotation,
    axial_retention,
):
    obj["ATTACHES_TO"] = attaches_to
    obj["FASTENER"] = fastener
    obj["LOAD_SURFACES"] = load_surfaces
    obj["INSTALLATION"] = install
    obj["REMOVAL"] = removal
    obj["TOOL_ACCESS"] = tool
    obj["ANTI_ROTATION"] = anti_rotation
    obj["AXIAL_RETENTION"] = axial_retention
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


def slot_cut(base, center, axis, slot_direction, slot_length, diameter, mat, coll="00_REFERENCE"):
    axis = Vector(axis).normalized()
    slot_direction = Vector(slot_direction).normalized()
    cross = axis.cross(slot_direction).normalized()
    cutter = oriented_box(
        base.name + "_SLOT_CUT",
        (slot_length, diameter, max(base.dimensions) + 8.0),
        center,
        slot_direction,
        axis,
        mat,
        coll,
        bevel=diameter / 2.0,
    )
    boolean_difference(base, cutter, "Alignment adjustment slot")


def strut_between(name, a, b, diameter, mat, coll, parent=None, export=False, quantity=1):
    a, b = Vector(a), Vector(b)
    obj = cylinder(name, diameter / 2.0, (b - a).length, (a + b) / 2.0, mat, coll, parent, vertices=32, bevel=0.5)
    orient_local_z(obj, b - a)
    if export:
        print_meta(obj, orientation="axis horizontal; add 5 mm brim tabs", walls=6, infill=45, supports=False, brim=True, quantity=quantity)
    return obj


def recalculate_constructed_normals(mesh) -> None:
    """Set outward winding while the parameter mesh is still source geometry."""
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


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
    recalculate_constructed_normals(mesh)
    obj = bpy.data.objects.new(name, mesh)
    collection(coll).objects.link(obj)
    obj.parent = parent
    assign_material(obj, mat)
    apply_bevel(obj, 0.6, 3)
    if export:
        print_meta(obj, orientation="flat on bed", walls=6, infill=45, supports=False, brim=False, quantity=quantity)
    return obj


def oriented_box(name, dims, center, x_axis, z_axis, mat, coll, parent=None, bevel=0.4):
    obj = box(name, dims, center, mat, coll, parent, bevel)
    x_axis = Vector(x_axis).normalized()
    z_axis = Vector(z_axis).normalized()
    y_axis = z_axis.cross(x_axis).normalized()
    x_axis = y_axis.cross(z_axis).normalized()
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Matrix((x_axis, y_axis, z_axis)).transposed().to_quaternion()
    return obj


def cube_edge_point(edge_axis, sign_a, sign_b, t, radius):
    if edge_axis == "X":
        raw = Vector((t, sign_a, sign_b))
    elif edge_axis == "Y":
        raw = Vector((sign_a, t, sign_b))
    else:
        raw = Vector((sign_a, sign_b, t))
    return raw.normalized() * radius


def cube_edge_frame(edge_axis, sign_a, sign_b, t, radius):
    center = cube_edge_point(edge_axis, sign_a, sign_b, t, radius)
    dt = 0.002
    tangent = (
        cube_edge_point(edge_axis, sign_a, sign_b, t + dt, radius)
        - cube_edge_point(edge_axis, sign_a, sign_b, t - dt, radius)
    ).normalized()
    radial = center.normalized()
    across = radial.cross(tangent).normalized()
    return center, tangent, across, radial


def curved_edge_prism(
    name,
    edge_axis,
    sign_a,
    sign_b,
    radius,
    half_width,
    radial_inner,
    radial_outer,
    t0,
    t1,
    mat,
    coll,
    parent=None,
    steps=18,
):
    verts = []
    faces = []
    for index in range(steps + 1):
        t = t0 + (t1 - t0) * index / steps
        center = cube_edge_point(edge_axis, sign_a, sign_b, t, radius)
        dt = 0.002
        tangent = (
            cube_edge_point(edge_axis, sign_a, sign_b, min(t1, t + dt), radius)
            - cube_edge_point(edge_axis, sign_a, sign_b, max(t0, t - dt), radius)
        ).normalized()
        radial = center.normalized()
        across = radial.cross(tangent).normalized()
        for radial_offset, side in (
            (radial_inner, -half_width),
            (radial_inner, half_width),
            (radial_outer, half_width),
            (radial_outer, -half_width),
        ):
            verts.append(tuple(radial * radial_offset + across * side))
    for index in range(steps):
        a = index * 4
        b = (index + 1) * 4
        faces.extend([
            (a, b, b + 1, a + 1),
            (a + 1, b + 1, b + 2, a + 2),
            (a + 2, b + 2, b + 3, a + 3),
            (a + 3, b + 3, b, a),
        ])
    faces.extend([(0, 1, 2, 3), (steps * 4, steps * 4 + 3, steps * 4 + 2, steps * 4 + 1)])
    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(verts, [], faces)
    recalculate_constructed_normals(mesh)
    obj = bpy.data.objects.new(name, mesh)
    collection(coll).objects.link(obj)
    obj.parent = parent
    assign_material(obj, mat)
    return obj


def gear_sector(name, pitch_radius, module, span_deg, height, z, mat, coll, parent=None):
    tooth_pitch = math.pi * module
    tooth_count = max(12, round(math.radians(span_deg) * pitch_radius / tooth_pitch))
    root_r = pitch_radius - 1.25 * module
    tip_r = pitch_radius + module
    inner_r = pitch_radius - 7.0
    a0 = math.radians(-90.0 - span_deg / 2.0)
    a1 = math.radians(-90.0 + span_deg / 2.0)
    outline = []
    for index in range(tooth_count * 4 + 1):
        fraction = index / (tooth_count * 4)
        angle = a0 + (a1 - a0) * fraction
        phase = index % 4
        radius = root_r if phase in (0, 3) else tip_r
        outline.append((radius * math.cos(angle), radius * math.sin(angle)))
    for index in range(tooth_count * 2, -1, -1):
        angle = a0 + (a1 - a0) * index / (tooth_count * 2)
        outline.append((inner_r * math.cos(angle), inner_r * math.sin(angle)))
    verts = [(x, y, z - height / 2.0) for x, y in outline] + [(x, y, z + height / 2.0) for x, y in outline]
    count = len(outline)
    faces = [tuple(range(count - 1, -1, -1)), tuple(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection(coll).objects.link(obj)
    obj.parent = parent
    assign_material(obj, mat)
    obj["GEAR_MODULE_MM"] = module
    obj["GEAR_TEETH"] = tooth_count
    return obj


def spur_gear(name, teeth, module, height, loc, mat, coll, parent=None):
    pitch_r = teeth * module / 2.0
    root_r = max(2.0, pitch_r - 1.25 * module)
    tip_r = pitch_r + module
    outline = []
    for index in range(teeth * 4):
        angle = 2.0 * math.pi * index / (teeth * 4)
        radius = root_r if index % 4 in (0, 3) else tip_r
        outline.append((loc[0] + radius * math.cos(angle), loc[1] + radius * math.sin(angle)))
    verts = [(x, y, loc[2] - height / 2.0) for x, y in outline] + [(x, y, loc[2] + height / 2.0) for x, y in outline]
    count = len(outline)
    faces = [tuple(range(count - 1, -1, -1)), tuple(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection(coll).objects.link(obj)
    obj.parent = parent
    assign_material(obj, mat)
    return obj


def fastener_cylinder(name, diameter, length, loc, axis, mat, parent=None, note=""):
    obj = cylinder(name, diameter / 2.0, length, loc, mat, "06_FASTENERS", parent, vertices=32, bevel=0.15)
    orient_local_z(obj, Vector(axis))
    obj["FASTENER_SPEC"] = note
    link_to_collection(obj, "FASTENERS")
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
        status="BLOCKED",
        placeholders="all seam inserts, drop coupon and full mesh collision validation",
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
    inner_r = outer_r - wall
    for target, diameter, depth, center_r in (
        (base, 2.8, wall + 5.0, outer_r - wall / 2.0),
        (grip, 2.8, 5.0, outer_r - float(CFG["tpu_grip_thickness_mm"]) / 2.0 - 0.15),
    ):
        screw_cut = cylinder(f"{target.name}_LOCK_CUT", diameter / 2.0, depth, direction * center_r, mat, "00_REFERENCE", vertices=32, bevel=0)
        orient_local_z(screw_cut, direction)
        boolean_difference(target, screw_cut, "TPU mechanical retention screw")
    carrier = tangent_box(
        f"TPU_GRIP_NUT_PLATE_{index:02d}",
        (float(CFG["tpu_grip_length_mm"]) + 4.0, float(CFG["tpu_grip_width_mm"]) + 4.0),
        3.0,
        direction,
        inner_r - 1.5,
        mat,
        "07_GRIP",
        parent,
        bevel=1.5,
    )
    insert_cut = cylinder(f"{carrier.name}_INSERT_CUT", 1.7, 4.0, direction * (inner_r - 1.5), mat, "00_REFERENCE", vertices=32, bevel=0)
    orient_local_z(insert_cut, direction)
    boolean_difference(carrier, insert_cut, "M2.5 insert well PLACEHOLDER")
    if index == 1:
        print_meta(carrier, orientation="largest flat face on bed", walls=4, infill=80, supports=False, brim=False, quantity=24, status="BLOCKED", placeholders="M2.5 insert and screw")
    fastener_cylinder(
        f"TPU_GRIP_SCREW_{index:02d}", 5.0, 2.0,
        direction * (outer_r - 0.6), direction, mat, parent,
        "M2.5 countersunk screw into internal nut plate",
    )
    mechanical_connection(
        grip,
        carrier.name,
        "1x countersunk M2.5 screw",
        "recess floor + dogbone pocket walls",
        "place insert in pocket, install screw from outside",
        "remove one screw; replace insert independently",
        "2 mm hex driver",
        "rectangular pocket walls",
        "M2.5 screw and internal nut plate",
    )
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


def cable_route(name, points, diameter, mat, coll, parent=None, collision_group="WIRE_ENVELOPE"):
    curve = bpy.data.curves.new(name + "_CURVE", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = diameter / 2.0
    curve.bevel_resolution = 3
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, co in zip(spline.points, points):
        point.co = (*co, 1.0)
    obj = bpy.data.objects.new(name, curve)
    collection(coll).objects.link(obj)
    obj.parent = parent
    assign_material(obj, mat)
    obj["COLLISION_GROUP"] = collision_group
    obj["MIN_BEND_RADIUS_MM"] = CFG["wire_min_bend_radius_mm"]
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


def collision_sweep_v2(inner_r: float, parent, yellow):
    """Visualization/broad phase only; final status comes from validate_robot.py BVH meshes."""
    arm = max(float(value) for value in CFG["pendulum_arm_radii_mm"])
    holder_r = float(CFG["ballast_holder_outer_diameter_mm"]) / 2.0
    bpy.ops.mesh.primitive_torus_add(
        major_radius=arm,
        minor_radius=holder_r,
        major_segments=96,
        minor_segments=24,
        rotation=(0, math.radians(90), 0),
    )
    swept = bpy.context.object
    swept.name = "PENDULUM_BALLAST_BROAD_PHASE"
    move_to_collection(swept, "09_COLLISION_ENVELOPES")
    link_to_collection(swept, "COLLISION")
    assign_material(swept, yellow)
    swept.parent = parent
    swept.hide_render = True
    arm_env = cylinder(
        "PENDULUM_FORK_BROAD_PHASE",
        arm + 7.0,
        50.0,
        (0, 0, 0),
        yellow,
        "09_COLLISION_ENVELOPES",
        parent,
        vertices=96,
        rotation=(0, math.radians(90), 0),
        bevel=0,
    )
    link_to_collection(arm_env, "COLLISION")
    arm_env.hide_render = True
    bpy.context.scene["broad_phase_status"] = "CANDIDATE_ONLY_NOT_A_PASS"
    bpy.context.scene["broad_phase_radial_reserve_mm"] = round(inner_r - arm - holder_r, 3)
    return swept, arm_env


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
        zero_area_faces = 0
        for face in bm.faces:
            key = tuple(sorted(vertex.index for vertex in face.verts))
            if key in face_keys:
                duplicate_faces += 1
            face_keys.add(key)
            if face.calc_area() <= 1e-8:
                zero_area_faces += 1
        non_manifold_edges = [edge for edge in bm.edges if not edge.is_manifold]
        non_manifold = len(non_manifold_edges)
        non_manifold_face_counts = [len(edge.link_faces) for edge in non_manifold_edges]
        zero_length_edges = sum(1 for edge in bm.edges if edge.calc_length() <= 1e-6)
        loose_edges = sum(1 for edge in bm.edges if not edge.link_faces)
        loose_vertices = sum(1 for vertex in bm.verts if not vertex.link_edges)
        quantized = {}
        duplicate_vertices = 0
        for vertex in bm.verts:
            key = tuple(round(value, 6) for value in vertex.co)
            if key in quantized:
                duplicate_vertices += 1
            quantized[key] = True
        signed_volume = bm.calc_volume(signed=True) if bm.faces else 0.0
        bm.free()
        eval_obj.to_mesh_clear()
        ok = (
            non_manifold == 0
            and duplicate_faces == 0
            and duplicate_vertices == 0
            and zero_area_faces == 0
            and zero_length_edges == 0
            and loose_edges == 0
            and loose_vertices == 0
            and signed_volume > 0.01
        )
        report["objects"][obj.name] = {
            "manifold": non_manifold == 0,
            "watertight": non_manifold == 0,
            "normals_outward": signed_volume > 0.0,
            "non_manifold_edges": non_manifold,
            "non_manifold_face_counts": non_manifold_face_counts,
            "duplicate_faces": duplicate_faces,
            "duplicate_vertices": duplicate_vertices,
            "zero_area_faces": zero_area_faces,
            "zero_length_edges": zero_length_edges,
            "loose_edges": loose_edges,
            "loose_vertices": loose_vertices,
            "volume_mm3": round(signed_volume, 2),
            "valid": ok,
        }
        report["all_manifold"] = report["all_manifold"] and ok
    return report


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
    stale = set(RENDER_DIR.glob("*.png"))
    all_state = {obj.name: obj.hide_render for obj in bpy.data.objects}

    def assembly_visibility(shell=True, collision=False):
        for obj in bpy.data.objects:
            if obj.type not in {"CAMERA", "LIGHT"}:
                obj.hide_render = True
        for name in ("01_SHELL", "02_FIXED_FRAME", "03_STEERING", "04_PENDULUM", "05_ELECTRONICS", "06_FASTENERS", "07_GRIP"):
            if name == "01_SHELL" and not shell:
                continue
            for obj in collection(name).all_objects:
                if not obj.name.startswith("EXP_"):
                    obj.hide_render = False
        if collision:
            for obj in collection("09_COLLISION_ENVELOPES").all_objects:
                obj.hide_render = False
            marker = bpy.data.objects.get("COLLISION_MINIMUM_MARKER")
            if marker:
                marker.hide_render = False
        for name in ("KEY_LIGHT", "FILL_LIGHT", "RIM_LIGHT", "FLOOR_REFERENCE"):
            if bpy.data.objects.get(name):
                bpy.data.objects[name].hide_render = False

    assembly_visibility(shell=True)
    render_scene(RENDER_DIR / "overview.png", (380, -380, 285), (0, 0, 0), 720)
    render_scene(RENDER_DIR / "transparent_assembly.png", (350, -350, 250), (0, 0, 0), 720)

    panel_state = {obj.name: obj.hide_render for obj in panel_objects}
    for obj in panel_objects:
        if obj.get("PANEL_AXIS") in {"+X", "+Y"}:
            obj.hide_render = True
    render_scene(RENDER_DIR / "section_view.png", (355, -355, 235), (0, 0, 0), 720)
    for obj in panel_objects:
        obj.hide_render = panel_state[obj.name]

    saved_locs = {obj.name: obj.location.copy() for obj in panel_objects}
    labels = []
    for number, obj in enumerate(panel_objects, start=1):
        direction = face_vector(obj.get("PANEL_AXIS"), 0, 0)
        obj.location += direction * 72.0
        label = add_text(f"EXPLODED_LABEL_{number:02d}", str(number), direction * 214.0, 16, bpy.data.materials["MAT_STEEL_DARK"], "00_REFERENCE")
        label.hide_render = False
        labels.append(label)
    render_scene(RENDER_DIR / "exploded_numbered.png", (455, -455, 340), (0, 0, 0), 800)
    for obj in panel_objects:
        obj.location = saved_locs[obj.name]
    for label in labels:
        bpy.data.objects.remove(label, do_unlink=True)

    assembly_visibility(shell=False)
    render_scene(RENDER_DIR / "load_path.png", (335, -335, 180), (0, 0, -15), 720)
    render_scene(RENDER_DIR / "shaft_assembly.png", (285, -235, 105), (0, 0, -8), 720)
    render_scene(RENDER_DIR / "steering_mechanism.png", (210, -310, 185), (0, 0, 0), 720)

    assembly_visibility(shell=True)
    for obj in panel_objects:
        if obj.get("PANEL_AXIS") in {"+X", "+Y", "+Z"}:
            obj.hide_render = True
    render_scene(RENDER_DIR / "shell_connections.png", (310, -310, 110), (75, 75, 20), 720)
    render_scene(RENDER_DIR / "electronics_layout.png", (290, -290, 245), (0, 0, 25), 720)
    render_scene(RENDER_DIR / "cable_routing.png", (320, -320, 225), (0, 25, 15), 720)

    assembly_visibility(shell=False, collision=True)
    render_scene(RENDER_DIR / "collision_minimum.png", (340, -340, 220), (0, 0, 0), 720)

    for obj in bpy.data.objects:
        if obj.type not in {"CAMERA", "LIGHT"}:
            obj.hide_render = True
    for name in ("KEY_LIGHT", "FILL_LIGHT", "RIM_LIGHT"):
        bpy.data.objects[name].hide_render = False
    print_parts = [duplicate for _source, duplicate, *_rest in export_objects]
    layout_parts = [obj for obj in print_parts if obj.get("SOURCE_OBJECT") in {
        "M3_TEST_COUPON", "BEARING_FIT_COUPON", "SHAFT_ALIGNMENT_JIG",
        "PENDULUM_TEST_STAND_BASE", "SILICONE_GRIP_TEMPLATE", "SEGMENT_ALIGNMENT_TEMPLATE",
    }]
    saved_layout = {obj.name: obj.location.copy() for obj in layout_parts}
    for obj, location in zip(layout_parts, ((-130, 70, 0), (0, 70, 0), (130, 70, 0), (-100, -70, 0), (35, -70, 0), (140, -70, 0))):
        obj.location = location
        obj.hide_render = False
    render_scene(RENDER_DIR / "print_orientation.png", (0, 0, 720), (0, 0, 0), 800)
    for obj in layout_parts:
        obj.location = saved_layout[obj.name]

    must_buy = [
        "SHAFT", "BEARING_LEFT_PLACEHOLDER", "BEARING_RIGHT_PLACEHOLDER",
        "SHAFT_COLLAR_LEFT_PLACEHOLDER", "SHAFT_COLLAR_RIGHT_PLACEHOLDER",
        "FLEXIBLE_COUPLING_METAL_PLACEHOLDER", "MAIN_MOTOR_GEARBOX_PLACEHOLDER",
        "PENDULUM_ENCODER_SENSOR_PLACEHOLDER", "BALLAST_300G_PLACEHOLDER",
    ]
    for obj in bpy.data.objects:
        if obj.type not in {"CAMERA", "LIGHT"}:
            obj.hide_render = True
    buy_objects = [bpy.data.objects.get(name) for name in must_buy if bpy.data.objects.get(name)]
    buy_state = {obj.name: (obj.location.copy(), obj.parent) for obj in buy_objects}
    for index, obj in enumerate(buy_objects):
        obj.parent = None
        obj.location = ((index % 3 - 1) * 95, (1 - index // 3) * 85, 0)
        obj.hide_render = False
    render_scene(RENDER_DIR / "must_buy_parts.png", (0, 0, 650), (0, 0, 0), 800)
    for obj in buy_objects:
        obj.location, obj.parent = buy_state[obj.name]

    required = {
        "overview.png", "transparent_assembly.png", "section_view.png", "exploded_numbered.png",
        "load_path.png", "shaft_assembly.png", "steering_mechanism.png", "shell_connections.png",
        "electronics_layout.png", "cable_routing.png", "collision_minimum.png",
        "print_orientation.png", "must_buy_parts.png",
    }
    for path in stale:
        if path.name not in required:
            path.unlink()
    for obj in bpy.data.objects:
        if obj.name in all_state:
            obj.hide_render = all_state[obj.name]


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
    panel_by_axis = {}
    grip_index = 1
    for idx, axis in enumerate(axes, start=1):
        safe_axis = axis.replace("+", "POS_").replace("-", "NEG_")
        panel = cube_sphere_panel(f"SHELL_SEGMENT_{idx:02d}_{safe_axis}", axis, outer_r, inner_r, int(CFG["shell_panel_grid"]), white, shell_root)
        panel_objects.append(panel)
        panel_by_axis[axis] = panel
        for uv in ((-0.48, -0.32), (-0.48, 0.32), (0.48, -0.32), (0.48, 0.32)):
            grip = grip_pocket(panel, axis, uv[0], uv[1], outer_r, wall, grey, tpu, grip_index, shell_root)
            if grip_index == 1:
                print_meta(grip, material_name="TPU 95A", orientation="flat outer face on bed", walls=3, infill=100, supports=False, brim=False, quantity=24, status="BLOCKED", placeholders="TPU availability, M2.5 retention hardware and protrusion test")
            grip_index += 1

    plus_x = panel_objects[0]
    hatch_opening = CFG["service_hatch_opening_mm"]
    hatch_cutter = tangent_box("SERVICE_HATCH_CUTTER", hatch_opening, wall + 10, (1, 0, 0), outer_r - wall / 2, grey, "00_REFERENCE", bevel=4)
    boolean_difference(plus_x, hatch_cutter, "Service hatch opening")
    hatch = tangent_box("SERVICE_HATCH", (hatch_opening[0] - 0.6, hatch_opening[1] - 0.6), 2.2, (1, 0, 0), outer_r - 1.7, white_solid, "01_SHELL", shell_root, bevel=3.6)
    print_meta(hatch, orientation="flat inner face on bed", walls=5, infill=30, supports=False, brim=False, status="PROTOTYPE_READY", placeholders="switch and charge connector cutouts")
    for y, z in ((-39, -23), (-39, 23), (39, -23), (39, 23)):
        screw = cylinder(f"SERVICE_HATCH_M3_{y}_{z}", 3.0, 3.0, (outer_r - 0.7, y, z), dark, "06_FASTENERS", shell_root, vertices=32, rotation=(0, math.radians(90), 0), bevel=0.2)
        screw["FASTENER"] = "M3 flush head"
    charge = box("CHARGE_CONNECTOR_PLACEHOLDER", (8, 12, 8), (outer_r - 4, -20, 0), dark, "05_ELECTRONICS", electronics_root, bevel=1.0)
    switch = box("MAIN_SWITCH_PLACEHOLDER", (8, 19.2, 13), (outer_r - 4, 20, 0), dark, "05_ELECTRONICS", electronics_root, bevel=1.0)

    # All 12 cube-sphere edges: internal flange, matching panel pockets,
    # two anti-shear keys and one recessed M3 fastener per adjacent panel.
    seam_specs = []
    for sy in (-1, 1):
        for sz in (-1, 1):
            seam_specs.append(("X", sy, sz, "+Y" if sy > 0 else "-Y", "+Z" if sz > 0 else "-Z"))
    for sx in (-1, 1):
        for sz in (-1, 1):
            seam_specs.append(("Y", sx, sz, "+X" if sx > 0 else "-X", "+Z" if sz > 0 else "-Z"))
    for sx in (-1, 1):
        for sy in (-1, 1):
            seam_specs.append(("Z", sx, sy, "+X" if sx > 0 else "-X", "+Y" if sy > 0 else "-Y"))
    face_centers = {
        "+X": Vector((1, 0, 0)), "-X": Vector((-1, 0, 0)),
        "+Y": Vector((0, 1, 0)), "-Y": Vector((0, -1, 0)),
        "+Z": Vector((0, 0, 1)), "-Z": Vector((0, 0, -1)),
    }
    seam_flanges = []
    seam_keys = []
    for seam_index, (edge_axis, sign_a, sign_b, panel_a_axis, panel_b_axis) in enumerate(seam_specs, start=1):
        flange = curved_edge_prism(
            f"SHELL_SEAM_FLANGE_{seam_index:02d}", edge_axis, sign_a, sign_b, inner_r,
            float(CFG["shell_seam_flange_width_mm"]) / 2.0,
            inner_r - float(CFG["shell_seam_flange_depth_mm"]), inner_r - 0.45,
            -1.0 + float(CFG["shell_seam_end_margin_ratio"]),
            1.0 - float(CFG["shell_seam_end_margin_ratio"]),
            grey, "01_SHELL", shell_root,
        )
        seam_flanges.append(flange)
        if seam_index == 1:
            print_meta(flange, orientation="curved flange on broad inner face", walls=6, infill=55, supports=False, brim=True, quantity=12, status="BLOCKED", placeholders="M3 heat insert pilot diameter")
        mechanical_connection(
            flange,
            f"{panel_a_axis} panel + {panel_b_axis} panel",
            "2x recessed M3 screws into heat inserts",
            "20 mm curved internal flange + panel edge walls",
            "place flange inside seam, insert two keys, tighten screws alternately",
            "remove the two panel screws; flange stays on adjacent panel",
            "2.5 mm hex driver from outside",
            "two keyed pockets and continuous curved flange",
            "M3 screws; flange captured between panels",
        )

        for key_number, key_t in enumerate((-0.34, 0.34), start=1):
            for panel_axis in (panel_a_axis, panel_b_axis):
                pocket = curved_edge_prism(
                    f"SEAM_{seam_index:02d}_KEY_{key_number}_{panel_axis}_CUTTER",
                    edge_axis, sign_a, sign_b, inner_r,
                    float(CFG["shell_seam_ridge_width_mm"]) / 2.0 + 0.15,
                    inner_r - 0.25,
                    inner_r + float(CFG["shell_seam_groove_depth_mm"]),
                    key_t - 0.075, key_t + 0.075,
                    grey, "00_REFERENCE", None, steps=4,
                )
                boolean_difference(panel_by_axis[panel_axis], pocket, f"Seam {seam_index} key pocket")
            key_obj = curved_edge_prism(
                f"SHELL_ALIGNMENT_KEY_{seam_index:02d}_{key_number}",
                edge_axis, sign_a, sign_b, inner_r,
                float(CFG["shell_seam_ridge_width_mm"]) / 2.0 - 0.15,
                inner_r - 0.15, inner_r + float(CFG["shell_seam_ridge_height_mm"]),
                key_t - 0.07, key_t + 0.07,
                grey, "01_SHELL", shell_root, steps=4,
            )
            seam_keys.append(key_obj)
            if seam_index == 1 and key_number == 1:
                print_meta(key_obj, orientation="largest flat face on bed", walls=5, infill=90, supports=False, brim=False, quantity=24, status="BLOCKED", placeholders="panel fit coupon")

        for screw_number, (panel_axis, screw_t) in enumerate(((panel_a_axis, -0.55), (panel_b_axis, 0.55)), start=1):
            _, _, across, radial = cube_edge_frame(edge_axis, sign_a, sign_b, screw_t, inner_r)
            offset_sign = 1.0 if across.dot(face_centers[panel_axis]) > 0.0 else -1.0
            offset = across * (5.0 * offset_sign)
            panel_hole_center = radial * (outer_r - wall / 2.0) + offset
            hole = cylinder(f"SEAM_{seam_index:02d}_PANEL_HOLE_{screw_number}", float(CFG["m3_clearance_mm"]) / 2.0, wall + 8.0, panel_hole_center, grey, "00_REFERENCE", vertices=48, bevel=0)
            orient_local_z(hole, radial)
            boolean_difference(panel_by_axis[panel_axis], hole, f"Seam {seam_index} M3 clearance")
            head = cylinder(f"SEAM_{seam_index:02d}_HEAD_{screw_number}", float(CFG["m3_counterbore_diameter_mm"]) / 2.0, 2.0, radial * (outer_r - 0.8) + offset, grey, "00_REFERENCE", vertices=48, bevel=0)
            orient_local_z(head, radial)
            boolean_difference(panel_by_axis[panel_axis], head, f"Seam {seam_index} flush head")
            insert_center = radial * (inner_r - 3.0) + offset
            insert_cut = cylinder(f"SEAM_{seam_index:02d}_INSERT_{screw_number}", float(CFG["m3_heat_insert_hole_mm_PLACEHOLDER"]) / 2.0, 7.0, insert_center, grey, "00_REFERENCE", vertices=48, bevel=0)
            orient_local_z(insert_cut, radial)
            boolean_difference(flange, insert_cut, f"Seam {seam_index} heat insert well")
            fastener_cylinder(
                f"SHELL_SEAM_M3_{seam_index:02d}_{screw_number}", 6.0, 3.0,
                radial * (outer_r - 0.7) + offset, radial, dark, shell_root,
                "M3 low-profile countersunk screw; length after insert measurement",
            )

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

    for join_index, angle in enumerate((0, 90, 180, 270), start=1):
        a = math.radians(angle)
        radial = Vector((math.cos(a), math.sin(a), 0))
        tangent = Vector((-math.sin(a), math.cos(a), 0))
        join_plate = oriented_box(f"FIXED_RING_JOIN_PLATE_{join_index:02d}", (28, 14, 4), radial * 106, tangent, Vector((0, 0, 1)), grey, "02_FIXED_FRAME", fixed_root, bevel=1.2)
        if join_index == 1:
            print_meta(join_plate, orientation="largest flat face on bed", walls=6, infill=70, supports=False, brim=False, quantity=4, status="BLOCKED", placeholders="M3 insert pilot diameter")
        for screw_index, tangent_offset in enumerate((-8, 8), start=1):
            fastener_cylinder(f"FIXED_RING_JOIN_M3_{join_index:02d}_{screw_index}", 6.0, 4.0, radial * 106 + tangent * tangent_offset + Vector((0, 0, 2.5)), (0, 0, 1), dark, fixed_root, "M3x10 into captive nut/insert")
        mechanical_connection(join_plate, "two adjacent fixed-ring quadrants", "2x M3 screws", "overlapping quadrant end faces", "install from upper side", "remove two screws", "2.5 mm hex driver", "two separated screws", "screw preload")

    # Eight shell anchors spread pendulum reaction into reinforced panel areas.
    for anchor_index in range(int(CFG["frame_shell_anchor_count"])):
        angle = math.radians(22.5 + anchor_index * 45.0)
        radial = Vector((math.cos(angle), math.sin(angle), 0))
        tangent = Vector((-math.sin(angle), math.cos(angle), 0))
        owner_axis = ("+X" if radial.x > 0 else "-X") if abs(radial.x) > abs(radial.y) else ("+Y" if radial.y > 0 else "-Y")
        pad = oriented_box(
            f"SHELL_REINFORCEMENT_PAD_{anchor_index+1:02d}",
            (float(CFG["frame_shell_anchor_pad_mm"][0]), float(CFG["frame_shell_anchor_pad_mm"][1]), float(CFG["frame_shell_anchor_pad_mm"][2])),
            radial * (inner_r - 2.5), tangent, radial, grey, "02_FIXED_FRAME", fixed_root, bevel=2.0,
        )
        if anchor_index == 0:
            print_meta(pad, orientation="broad inner face on bed", walls=7, infill=70, supports=False, brim=True, quantity=8, status="BLOCKED", placeholders="M3 heat insert and shell coupon")
        standoff = strut_between(
            f"FRAME_SHELL_STANDOFF_{anchor_index+1:02d}", radial * 111.0, radial * (inner_r - 6.0), 9.0,
            grey, "02_FIXED_FRAME", fixed_root, export=(anchor_index == 0), quantity=8,
        )
        standoff["PRINT_STATUS"] = "BLOCKED"
        for screw_index, zoff in enumerate((-7.0, 7.0), start=1):
            panel_center = radial * (outer_r - wall / 2.0) + Vector((0, 0, zoff))
            panel_cut = cylinder(f"FRAME_ANCHOR_PANEL_CUT_{anchor_index+1:02d}_{screw_index}", float(CFG["m3_clearance_mm"]) / 2.0, wall + 8, panel_center, grey, "00_REFERENCE", vertices=48, bevel=0)
            orient_local_z(panel_cut, radial)
            boolean_difference(panel_by_axis[owner_axis], panel_cut, "Frame anchor M3 clearance")
            head_cut = cylinder(f"FRAME_ANCHOR_HEAD_CUT_{anchor_index+1:02d}_{screw_index}", float(CFG["m3_counterbore_diameter_mm"]) / 2.0, 2.0, radial * (outer_r - 0.8) + Vector((0, 0, zoff)), grey, "00_REFERENCE", vertices=48, bevel=0)
            orient_local_z(head_cut, radial)
            boolean_difference(panel_by_axis[owner_axis], head_cut, "Frame anchor flush head")
            pad_cut = cylinder(f"FRAME_ANCHOR_PAD_INSERT_{anchor_index+1:02d}_{screw_index}", float(CFG["m3_heat_insert_hole_mm_PLACEHOLDER"]) / 2.0, 6.0, radial * (inner_r - 2.5) + Vector((0, 0, zoff)), grey, "00_REFERENCE", vertices=48, bevel=0)
            orient_local_z(pad_cut, radial)
            boolean_difference(pad, pad_cut, "Frame anchor heat insert well")
            fastener_cylinder(f"FRAME_ANCHOR_M3_{anchor_index+1:02d}_{screw_index}", 6.0, 3.0, radial * (outer_r - 0.7) + Vector((0, 0, zoff)), radial, dark, shell_root, "M3 countersunk into reinforced pad")
        mechanical_connection(
            pad, owner_axis + " shell panel", "2x recessed M3 into heat inserts",
            "34x24 mm load spreader against inner shell",
            "fit pad, loosely attach standoff, tighten shell screws",
            "remove shell screws and inner standoff screw",
            "2.5 mm hex outside; ball-end hex inside",
            "two separated shell screws + keyed standoff face",
            "shell screws and standoff clamp",
        )
        mechanical_connection(
            standoff, f"FIXED_FRAME_RING and {pad.name}", "M3 screw at each end",
            "9 mm end faces",
            "install after fixed ring quadrants are joined",
            "remove two accessible radial screws",
            "ball-end 2.5 mm hex",
            "flat/indexed end faces",
            "two end screws",
        )

    # Steering frame: four adjustable sliding-bearing carriers, axial retainers,
    # printed gear sector, TT pinion and independent angle feedback.
    steering_ring = ring("STEERING_RING", float(CFG["steering_ring_outer_diameter_mm"]), float(CFG["steering_ring_inner_diameter_mm"]), 8, (0, 0, 0), orange, "03_STEERING", steering_root, export=False)
    notch = box("STEERING_RING_MOTOR_NOTCH", (62, 58, 18), (-68, 0, 0), grey, "00_REFERENCE", bevel=0)
    boolean_difference(steering_ring, notch, "Main motor replacement opening")
    print_meta(steering_ring, orientation="flat on bed", walls=7, infill=50, supports=False, brim=True, status="BLOCKED", placeholders="yaw-pad fit and TT backlash")
    steering_ring["YAW_RANGE_DEG"] = [-float(CFG["steering_limit_deg"]), float(CFG["steering_limit_deg"])]
    steering_ring["COLLISION_GROUP"] = "STEERING_DYNAMIC"
    mechanical_connection(steering_ring, "FIXED_FRAME_RING", "4 radial pad carriers + 4 axial retainers", "190 mm guide circumference and axial lips", "insert from open shell before retainers", "remove four retainers and motor pinion", "2.5 mm hex", "four radial supports", "top/bottom axial retainer pairs")

    for pad_index, angle_deg in enumerate((0, 90, 180, 270), start=1):
        angle = math.radians(angle_deg)
        radial = Vector((math.cos(angle), math.sin(angle), 0))
        tangent = Vector((-math.sin(angle), math.cos(angle), 0))
        carrier = oriented_box(f"YAW_PAD_CARRIER_{pad_index:02d}", (24, 10, 20), radial * 100.5, tangent, Vector((0, 0, 1)), grey, "02_FIXED_FRAME", fixed_root, bevel=1.5)
        pad = oriented_box(f"YAW_BEARING_PAD_{pad_index:02d}", (18, 3.0, 12), radial * (95.0 + float(CFG["steering_radial_pad_clearance_mm"]) + 1.5), tangent, Vector((0, 0, 1)), cyan, "02_FIXED_FRAME", fixed_root, bevel=0.6)
        if pad_index == 1:
            print_meta(carrier, orientation="broad face on bed", walls=6, infill=60, supports=False, brim=False, quantity=4, status="BLOCKED", placeholders="pad material and measured yaw clearance")
            print_meta(pad, material_name="PETG prototype; POM/PTFE optional", orientation="largest flat face on bed", walls=5, infill=100, supports=False, brim=False, quantity=4, status="PROTOTYPE_READY")
        mechanical_connection(carrier, "FIXED_FRAME_RING", "2x M3 screws in radial adjustment slots", "carrier foot and fixed ring", "set 0.35 mm feeler clearance and tighten", "remove two screws", "ball-end 2.5 mm hex", "two screws", "captured pad dovetail")
        mechanical_connection(pad, carrier.name, "dovetail slide + one M3 retaining screw", "18x12 mm sliding bearing face", "slide from top before axial retainer", "remove one screw and slide out", "2.5 mm hex", "dovetail", "retaining screw")

    for retainer_index, angle_deg in enumerate((45, 225), start=1):
        angle = math.radians(angle_deg)
        radial = Vector((math.cos(angle), math.sin(angle), 0))
        tangent = Vector((-math.sin(angle), math.cos(angle), 0))
        for side, z in (("TOP", 6.4), ("BOTTOM", -6.4)):
            retainer = oriented_box(f"YAW_RETAINER_{side}_{retainer_index:02d}", (32, 14, 3.2), radial * 94.5 + Vector((0, 0, z)), tangent, Vector((0, 0, 1)), grey, "02_FIXED_FRAME", fixed_root, bevel=1.0)
            if retainer_index == 1 and side == "TOP":
                print_meta(retainer, orientation="flat on bed", walls=6, infill=70, supports=False, brim=False, quantity=4, status="BLOCKED", placeholders="measured axial clearance")
            mechanical_connection(retainer, "FIXED_FRAME_RING", "2x M3 screws", "overlap on steering-ring axial lip with 0.4 mm clearance", "set feeler gap then tighten", "remove two screws", "2.5 mm hex", "two screws", "captures steering ring axially")

    steering_sector = gear_sector("STEERING_GEAR_SECTOR", float(CFG["steering_gear_pitch_radius_mm"]), float(CFG["steering_gear_module_mm"]), float(CFG["steering_gear_sector_deg"]), 6.0, -10.0, orange, "03_STEERING", steering_root)
    print_meta(steering_sector, orientation="flat gear face on bed", walls=7, infill=70, supports=False, brim=True, status="BLOCKED", placeholders="TT speed, torque and backlash test")
    steering_sector["COLLISION_GROUP"] = "STEERING_DYNAMIC"
    for sector_screw, angle_deg in enumerate((-145, -115, -65, -35), start=1):
        a = math.radians(angle_deg)
        fastener_cylinder(f"STEERING_SECTOR_M3_{sector_screw:02d}", 6.0, 6.0, (92 * math.cos(a), 92 * math.sin(a), -6.0), (0, 0, 1), dark, steering_root, "M3 through sector spacer into steering ring insert")
    mechanical_connection(steering_sector, "STEERING_RING", "4x M3 screws with printed spacers", "four sector mounting pads", "install from lower side before yaw retainers", "remove four screws", "2.5 mm hex", "four spaced screws", "screw preload")

    steering_pinion = spur_gear("STEERING_PINION", int(CFG["steering_pinion_teeth"]), float(CFG["steering_gear_module_mm"]), 8.0, (0, -108, -10), orange, "02_FIXED_FRAME", fixed_root)
    pinion_bore = cylinder("STEERING_PINION_D_BORE", float(CFG["tt_motor_d_shaft_round_mm_USER_REPORTED"]) / 2.0 + 0.15, 12.0, (0, -108, -10), grey, "00_REFERENCE", vertices=48, bevel=0)
    boolean_difference(steering_pinion, pinion_bore, "TT D-shaft prototype bore")
    print_meta(steering_pinion, orientation="flat gear face on bed", walls=6, infill=100, supports=False, brim=False, status="BLOCKED", placeholders="measured TT D-flat and backlash")
    yaw_mount = drilled_box("STEERING_TT_MOTOR_MOUNT", (76, 34, 6), (0, -111, -31), [((-28, -10, 0), 3.4, (0, 0, 1)), ((28, -10, 0), 3.4, (0, 0, 1)), ((-28, 10, 0), 3.4, (0, 0, 1)), ((28, 10, 0), 3.4, (0, 0, 1))], grey, "02_FIXED_FRAME", fixed_root, bevel=1.2)
    slot_cut(yaw_mount, (-24, -111, -31), (0, 0, 1), (0, 1, 0), 8.0, 3.4, grey)
    slot_cut(yaw_mount, (24, -111, -31), (0, 0, 1), (0, 1, 0), 8.0, 3.4, grey)
    print_meta(yaw_mount, orientation="flat base on bed", walls=6, infill=50, supports=False, brim=False, status="BLOCKED", placeholders="TT mounting holes and shaft position")
    tt_motor = box("STEERING_TT_MOTOR_USER_REPORTED", (65, 23, 20), (0, -111, -20), dark, "05_ELECTRONICS", fixed_root, bevel=2.0)
    tt_motor["COLLISION_GROUP"] = "FIXED_OBSTACLE"
    link_to_collection(tt_motor, "PLACEHOLDERS")
    mechanical_connection(tt_motor, yaw_mount.name, "2x measured TT clamp screws", "gearbox broad faces in printed cradle", "slide radially for backlash then tighten", "remove clamp and pinion", "2.5 mm hex", "D-shaft pinion + cradle walls", "motor clamp")

    steering_sensor = box("STEERING_ANGLE_SENSOR_PLACEHOLDER", CFG["steering_angle_sensor_size_mm_PLACEHOLDER"], (0, 103, 10), green, "05_ELECTRONICS", fixed_root, bevel=1.0)
    steering_magnet = cylinder("STEERING_ANGLE_MAGNET_PLACEHOLDER", 4.0, 2.0, (0, 96, 8), dark, "03_STEERING", steering_root, vertices=32, bevel=0.2)
    link_to_collection(steering_sensor, "PLACEHOLDERS")
    link_to_collection(steering_magnet, "PLACEHOLDERS")
    zero_pointer = box("STEERING_MANUAL_ZERO_POINTER", (2, 12, 6), (0, 100, 0), orange, "03_STEERING", steering_root, bevel=0.5)
    for side, angle in (("MIN", -65), ("MAX", 65)):
        a = math.radians(angle - 90)
        stop = box(f"STEERING_STOP_{side}", (10, 8, 14), (102 * math.cos(a), 102 * math.sin(a), 0), grey, "02_FIXED_FRAME", fixed_root, bevel=1.0)
        stop.rotation_euler.z = a
    steering_tab = box("STEERING_STOP_TAB", (12, 8, 16), (0, -98, 0), orange, "03_STEERING", steering_root, bevel=1.0)

    # Replaceable bearing carriers generated from one shaft axis and tied to the steering ring.
    bearing_xs = [float(value) for value in CFG["shaft_bearing_axis_x_mm"]]
    supports = []
    for side, x in (("LEFT", bearing_xs[0]), ("RIGHT", bearing_xs[1])):
        support = drilled_box(f"SHAFT_SUPPORT_{side}", (14, 50, 58), (x, 0, 0), [((0, 0, 0), float(CFG["bearing_carrier_outer_diameter_mm"]) + 0.3, (1, 0, 0))], orange, "03_STEERING", steering_root, bevel=1.5)
        slot_cut(support, (x, -18, -21), (1, 0, 0), (0, 0, 1), 8.0, 3.4, orange)
        slot_cut(support, (x, 18, -21), (1, 0, 0), (0, 0, 1), 8.0, 3.4, orange)
        print_meta(support, orientation="broad YZ face on bed", walls=8, infill=60, supports=False, brim=False, status="BLOCKED", placeholders="bearing carrier coupon and alignment")
        support["COLLISION_GROUP"] = "STEERING_DYNAMIC"
        supports.append(support)
        for sign_y in (-1, 1):
            target_y = sign_y * math.sqrt(89.0**2 - x**2)
            brace = strut_between(f"SHAFT_SUPPORT_{side}_BRACE_{'A' if sign_y < 0 else 'B'}", (x, sign_y * 22, -18), (x, target_y, 0), 8.0, orange, "03_STEERING", steering_root, export=(side == "LEFT" and sign_y < 0), quantity=4)
            brace["PRINT_STATUS"] = "BLOCKED"
            brace["COLLISION_GROUP"] = "STEERING_DYNAMIC"
        carrier = ring(f"BEARING_CARRIER_{side}", float(CFG["bearing_carrier_outer_diameter_mm"]), 21.8, 10.0, (x, 0, 0), orange, "03_STEERING", steering_root, export=False)
        carrier.rotation_euler.y = math.radians(90)
        print_meta(carrier, orientation="shoulder face on bed", walls=7, infill=75, supports=False, brim=False, status="BLOCKED", placeholders="actual bearing OD and press/slip fit")
        carrier["COLLISION_GROUP"] = "STEERING_DYNAMIC"
        retainer_x = x - 8.5 if x < 0 else x + 8.5
        retainer = ring(f"BEARING_RETAINER_{side}", 36.0, 24.0, 3.0, (retainer_x, 0, 0), orange, "03_STEERING", steering_root, export=False)
        retainer.rotation_euler.y = math.radians(90)
        print_meta(retainer, orientation="flat on bed", walls=6, infill=70, supports=False, brim=False, status="BLOCKED", placeholders="bearing width")
        for screw_index, zoff in enumerate((-12, 12), start=1):
            fastener_cylinder(f"BEARING_RETAINER_{side}_M3_{screw_index}", 5.5, 4.0, (retainer_x, 0, zoff), (1, 0, 0), dark, steering_root, "M3 retainer screw")
        mechanical_connection(carrier, support.name, "sliding carrier + retainer cap", "34 mm carrier OD and support bore shoulder", "press bearing in carrier, slide carrier into support", "remove retainer; use rear ejection ports", "2.5 mm hex and arbor press", "carrier shoulder", "removable retainer cap")

    bearing_size = CFG["bearing_size_mm_PLACEHOLDER"]
    for name, x in (("BEARING_LEFT_PLACEHOLDER", bearing_xs[0]), ("BEARING_RIGHT_PLACEHOLDER", bearing_xs[1])):
        bearing = cylinder(name, bearing_size[1] / 2.0, bearing_size[2], (x, 0, 0), dark, "03_STEERING", steering_root, vertices=64, rotation=(0, math.radians(90), 0), bevel=0.3)
        bore = cylinder(name + "_BORE", bearing_size[0] / 2.0, bearing_size[2] + 2, (x, 0, 0), dark, "00_REFERENCE", vertices=48, bevel=0)
        orient_local_z(bore, Vector((1, 0, 0)))
        boolean_difference(bearing, bore, "Bearing bore")
        bearing["COLLISION_GROUP"] = "STEERING_DYNAMIC"
        link_to_collection(bearing, "PLACEHOLDERS")

    # Main motor is isolated from radial load by the two bearings and a flexible coupling.
    motor_mount = drilled_box("MOTOR_MOUNT", (42, 54, 6), (-96, 0, -25), [((-15, -20, 0), 3.4, (0, 0, 1)), ((15, -20, 0), 3.4, (0, 0, 1)), ((-15, 20, 0), 3.4, (0, 0, 1)), ((15, 20, 0), 3.4, (0, 0, 1))], orange, "03_STEERING", steering_root, bevel=1.0)
    slot_cut(motor_mount, (-111, -20, -25), (0, 0, 1), (1, 0, 0), 8.0, 3.4, orange)
    slot_cut(motor_mount, (-81, 20, -25), (0, 0, 1), (1, 0, 0), 8.0, 3.4, orange)
    print_meta(motor_mount, orientation="flat base on bed", walls=7, infill=55, supports=False, brim=False, status="BLOCKED", placeholders="main motor body and mounting pattern")
    motor_clamp = drilled_box("MOTOR_CLAMP", (34, 8, 44), (-96, 0, -2), [((0, 0, -16), 3.4, (0, 1, 0)), ((0, 0, 16), 3.4, (0, 1, 0))], orange, "03_STEERING", steering_root, bevel=1.2)
    print_meta(motor_clamp, orientation="broad face on bed", walls=7, infill=55, supports=False, brim=False, status="BLOCKED", placeholders="main motor body")
    motor = box("MAIN_MOTOR_GEARBOX_PLACEHOLDER", CFG["main_motor_size_mm_PLACEHOLDER"], (-96, 0, -2), dark, "03_STEERING", steering_root, bevel=2)
    motor["REPLACEABLE"] = True
    motor["REQUIRED_SPEC"] = "50–70 rpm; continuous torque/current and thermal duty TBD; encoder required"
    motor["COLLISION_GROUP"] = "STEERING_DYNAMIC"
    link_to_collection(motor, "PLACEHOLDERS")
    encoder = cylinder("MAIN_MOTOR_ENCODER_PLACEHOLDER", 16, 12, (-118, 0, -2), green, "03_STEERING", steering_root, vertices=48, rotation=(0, math.radians(90), 0), bevel=0.6)
    encoder["COLLISION_GROUP"] = "STEERING_DYNAMIC"
    link_to_collection(encoder, "PLACEHOLDERS")
    encoder_guard = cylinder("ENCODER_GUARD", 19, 16, (-118, 0, -2), orange, "03_STEERING", steering_root, vertices=48, rotation=(0, math.radians(90), 0), bevel=0.8)
    guard_cut = cylinder("ENCODER_GUARD_CUT", 16.5, 18, (-118, 0, -2), orange, "00_REFERENCE", vertices=48, bevel=0)
    orient_local_z(guard_cut, Vector((1, 0, 0)))
    boolean_difference(encoder_guard, guard_cut, "Encoder cavity")
    print_meta(encoder_guard, orientation="open side upward", walls=5, infill=35, supports=False, brim=False, status="BLOCKED", placeholders="encoder envelope")
    coupling = cylinder("FLEXIBLE_COUPLING_PLACEHOLDER", float(CFG["flex_coupling_size_mm_PLACEHOLDER"][2]) / 2.0, float(CFG["flex_coupling_size_mm_PLACEHOLDER"][3]), (-72.5, 0, 0), dark, "04_PENDULUM", pendulum_axis, vertices=64, rotation=(0, math.radians(90), 0), bevel=0.4)
    coupling["COLLISION_GROUP"] = "PENDULUM_DYNAMIC"
    link_to_collection(coupling, "PLACEHOLDERS")
    for screw_index, x in enumerate((-67, -78), start=1):
        fastener_cylinder(f"COUPLING_CLAMP_SCREW_{screw_index}", 4.0, 10.0, (x, 0, 5.5), (0, 0, 1), dark, pendulum_axis, "coupling manufacturer clamp screw")
    coupling_guard = drilled_box("COUPLING_GUARD", (30, 32, 18), (-72.5, 0, 10), [((-11, -12, 0), 3.4, (0, 0, 1)), ((11, -12, 0), 3.4, (0, 0, 1))], orange, "03_STEERING", steering_root, bevel=2.0)
    guard_window = box("COUPLING_GUARD_WINDOW", (27, 25, 16), (-72.5, 0, 7), orange, "00_REFERENCE", bevel=2.0)
    boolean_difference(coupling_guard, guard_window, "Open underside and screw access")
    print_meta(coupling_guard, orientation="open side upward", walls=5, infill=35, supports=False, brim=False, status="BLOCKED", placeholders="coupling OD and clamp screw access")
    mechanical_connection(coupling, "main motor output shaft + 8 mm main shaft", "two industrial clamping hubs", "metal bores on both shafts with 2 mm face gap", "align motor, insert both shafts, tighten coupling clamps", "remove guard and loosen both clamps", "manufacturer hex key through guard window", "metal clamp bores/D-flat", "coupling clamps")

    # Steel shaft, two axial collars/spacers and dual split-clamp pendulum hubs.
    shaft = cylinder("SHAFT", float(CFG["shaft_diameter_mm"]) / 2.0, float(CFG["shaft_length_mm"]), (0, 0, 0), dark, "04_PENDULUM", pendulum_axis, vertices=64, rotation=(0, math.radians(90), 0), bevel=0.2)
    shaft["MATERIAL"] = "ground steel h6 preferred"
    shaft["COLLISION_GROUP"] = "PENDULUM_DYNAMIC"
    mechanical_connection(shaft, "bearing inner rings + flexible coupling + clamp hubs", "2 metal collars, coupling clamps and two split hubs", "8 mm cylindrical seats", "slide through right bearing before coupling", "remove coupling, collars and right retainer", "hex keys + soft drift", "clamp friction; optional shaft flat after motor selection", "two metal collars against inner-ring spacers")
    collar_size = CFG["shaft_collar_size_mm_PLACEHOLDER"]
    for side, x in (("LEFT", -41.0), ("RIGHT", 41.0)):
        spacer = cylinder(f"SHAFT_SPACER_{side}", 6.0, float(CFG["shaft_spacer_length_mm"]), (x - 4.8 if x < 0 else x + 4.8, 0, 0), dark, "04_PENDULUM", pendulum_axis, vertices=48, rotation=(0, math.radians(90), 0), bevel=0.1)
        collar = cylinder(f"SHAFT_COLLAR_{side}_PLACEHOLDER", float(collar_size[1]) / 2.0, float(collar_size[2]), (x, 0, 0), dark, "04_PENDULUM", pendulum_axis, vertices=64, rotation=(0, math.radians(90), 0), bevel=0.3)
        collar["COLLISION_GROUP"] = "PENDULUM_DYNAMIC"
        link_to_collection(collar, "PLACEHOLDERS")
        fastener_cylinder(f"SHAFT_COLLAR_{side}_CLAMP_SCREW", 4.0, 10.0, (x, 0, 5.0), (0, 0, 1), dark, pendulum_axis, "metal clamping collar screw")

    clamp_hubs = []
    arm_objects = []
    for side, x in (("LEFT", -18.0), ("RIGHT", 18.0)):
        hub = cylinder(f"PENDULUM_CLAMP_HUB_{side}", float(CFG["hub_clamp_outer_diameter_mm"]) / 2.0, float(CFG["hub_clamp_length_mm"]), (x, 0, 0), orange, "04_PENDULUM", pendulum_axis, vertices=64, rotation=(0, math.radians(90), 0), bevel=0.8)
        hub_bore = cylinder(f"PENDULUM_HUB_{side}_BORE", float(CFG["shaft_diameter_mm"]) / 2.0 + 0.12, float(CFG["hub_clamp_length_mm"]) + 4, (x, 0, 0), orange, "00_REFERENCE", vertices=48, bevel=0)
        orient_local_z(hub_bore, Vector((1, 0, 0)))
        boolean_difference(hub, hub_bore, "8 mm clamp bore")
        slit = box(f"PENDULUM_HUB_{side}_SLIT", (float(CFG["hub_clamp_length_mm"]) + 2, 2.0, 12.0), (x, 0, 10), orange, "00_REFERENCE", bevel=0)
        boolean_difference(hub, slit, "Split clamp slit")
        print_meta(hub, orientation="axis horizontal, slit upward", walls=9, infill=90, supports=False, brim=True, status="BLOCKED", placeholders="actual shaft diameter and clamp-capacity test", quantity=1)
        hub["COLLISION_GROUP"] = "PENDULUM_DYNAMIC"
        clamp_hubs.append(hub)
        for screw_index, zoff in enumerate((7.0, 11.0), start=1):
            fastener_cylinder(f"HUB_{side}_M4_CLAMP_{screw_index}", 7.0, 18.0, (x, 0, zoff), (0, 1, 0), dark, pendulum_axis, "M4 clamp screw with steel washer and captive nut")
        arm = drilled_box(f"PENDULUM_ARM_{side}", (8, 14, 74), (x, 0, -31), [((0, 0, 29), 4.5, (1, 0, 0)), ((0, 0, 21), 4.5, (1, 0, 0)), ((0, 0, -21), 4.5, (1, 0, 0)), ((0, 0, -29), 4.5, (1, 0, 0)), ((0, 0, -37), 4.5, (1, 0, 0))], orange, "04_PENDULUM", pendulum_axis, bevel=2.5)
        print_meta(arm, orientation="broad side on bed", walls=9, infill=75, supports=False, brim=True, status="BLOCKED", placeholders="ballast proof load and PETG coupon")
        arm["BALLAST_RADII_MM"] = CFG["pendulum_arm_radii_mm"]
        arm["COLLISION_GROUP"] = "PENDULUM_DYNAMIC"
        arm_objects.append(arm)
        for screw_index, zoff in enumerate((-2.0, -10.0), start=1):
            fastener_cylinder(f"ARM_{side}_TO_HUB_M4_{screw_index}", 7.0, 16.0, (x, 0, zoff), (1, 0, 0), dark, pendulum_axis, "M4 through bolt, steel washers, Nyloc nut")
        mechanical_connection(arm, hub.name, "2x M4 through bolts", "flat hub flange and arm root", "bolt arm to hub before installing ballast", "remove two bolts", "3 mm hex + 7 mm wrench", "two vertically separated bolts", "through bolts")
        mechanical_connection(hub, "SHAFT", "2x M4 split-clamp screws", "14 mm long 8 mm bore", "position symmetrically and torque both screws", "loosen both clamp screws", "3 mm hex + captive nuts", "split clamp friction; optional shaft flat", "clamp preload")

    saddle = drilled_box("BALLAST_SLIDER_SADDLE", (48, 26, 16), (0, 0, -60), [((-18, 0, 0), 4.5, (1, 0, 0)), ((18, 0, 0), 4.5, (1, 0, 0))], orange, "04_PENDULUM", pendulum_axis, bevel=3.0)
    print_meta(saddle, orientation="broad face on bed", walls=9, infill=80, supports=False, brim=True, status="BLOCKED", placeholders="arm station proof load")
    saddle["COLLISION_GROUP"] = "PENDULUM_DYNAMIC"
    for side, x in (("LEFT", -18), ("RIGHT", 18)):
        fastener_cylinder(f"BALLAST_STATION_M4_{side}", 7.0, 18.0, (x, 0, -60), (0, 1, 0), dark, pendulum_axis, "M4 shoulder bolt through selected arm station + Nyloc")
    saddle["DISCRETE_RADII_MM"] = CFG["pendulum_arm_radii_mm"]
    mechanical_connection(saddle, "PENDULUM_ARM_LEFT + PENDULUM_ARM_RIGHT", "2x M4 shoulder bolts + Nyloc", "keyed saddle faces on both fork arms", "align one discrete radius station and insert both bolts", "remove both bolts through service hatch", "3 mm hex + 7 mm wrench", "dual fork-arm engagement", "two Nyloc bolts")

    holder_length = float(CFG["ballast_holder_length_mm"])
    holder = cylinder("BALLAST_HOLDER", float(CFG["ballast_holder_outer_diameter_mm"]) / 2.0, holder_length, (0, 0, -60), orange, "04_PENDULUM", pendulum_axis, vertices=64, rotation=(0, math.radians(90), 0), bevel=0.8)
    cavity = cylinder("BALLAST_CAVITY", float(CFG["ballast_diameter_mm"]) / 2.0 + 0.3, holder_length - 3.0, (1.5, 0, -60), orange, "00_REFERENCE", vertices=64, bevel=0)
    orient_local_z(cavity, Vector((1, 0, 0)))
    boolean_difference(holder, cavity, "Steel ballast cavity")
    print_meta(holder, orientation="closed end on bed", walls=9, infill=65, supports=False, brim=True, status="BLOCKED", placeholders="measured steel ballast stack")
    holder["COLLISION_GROUP"] = "PENDULUM_DYNAMIC"
    lid_x = holder_length / 2.0 + 1.6
    lid = cylinder("BALLAST_LID", float(CFG["ballast_holder_outer_diameter_mm"]) / 2.0, 3.2, (lid_x, 0, -60), orange, "04_PENDULUM", pendulum_axis, vertices=64, rotation=(0, math.radians(90), 0), bevel=0.6)
    print_meta(lid, orientation="flat on bed", walls=7, infill=80, supports=False, brim=False, status="BLOCKED", placeholders="M3 insert and ballast stack")
    lid["COLLISION_GROUP"] = "PENDULUM_DYNAMIC"
    for screw_index, angle_deg in enumerate((0, 120, 240), start=1):
        angle = math.radians(angle_deg)
        y = 16.5 * math.cos(angle)
        z = -60 + 16.5 * math.sin(angle)
        lid_cut = cylinder(f"BALLAST_LID_HOLE_{screw_index}", float(CFG["m3_clearance_mm"]) / 2.0, 6.0, (lid_x, y, z), orange, "00_REFERENCE", vertices=40, bevel=0)
        orient_local_z(lid_cut, Vector((1, 0, 0)))
        boolean_difference(lid, lid_cut, "Ballast lid M3 clearance")
        holder_insert = cylinder(f"BALLAST_HOLDER_INSERT_{screw_index}", float(CFG["m3_heat_insert_hole_mm_PLACEHOLDER"]) / 2.0, 6.0, (holder_length / 2.0 - 2.5, y, z), orange, "00_REFERENCE", vertices=40, bevel=0)
        orient_local_z(holder_insert, Vector((1, 0, 0)))
        boolean_difference(holder, holder_insert, "Ballast lid heat insert")
        fastener_cylinder(f"BALLAST_LID_M3_{screw_index}", 6.0, 4.0, (lid_x + 1.5, y, z), (1, 0, 0), dark, pendulum_axis, "M3 screw into heat insert")
    safety_pin = fastener_cylinder("BALLAST_SECONDARY_RETENTION_PIN_PLACEHOLDER", 3.0, 54.0, (holder_length / 2.0 - 4.0, 0, -60), (0, 1, 0), dark, pendulum_axis, "steel cotter pin or safety wire through holder and lid tab")
    link_to_collection(safety_pin, "PLACEHOLDERS")
    mechanical_connection(holder, saddle.name, "4x M4 through bolts in two fork lugs", "48x26 mm keyed saddle interface", "bolt holder to saddle before loading steel", "park pendulum lid toward service hatch; remove four bolts", "3 mm hex + 7 mm wrench", "keyed saddle and four bolts", "four through bolts")
    mechanical_connection(lid, holder.name, "3x M3 screws + secondary steel pin", "annular 3.2 mm lid shoulder", "seat lid, tighten crosswise, fit pin", "park at service hatch, remove pin and three screws", "2.5 mm hex + pliers", "three screws at 120 degrees", "three screws and secondary pin")

    for mass in CFG["ballast_variants_g"]:
        length = float(mass) / (float(CFG["steel_density_g_cm3"]) * math.pi * (float(CFG["ballast_diameter_mm"]) / 20.0) ** 2) * 10.0
        ballast = cylinder(f"BALLAST_{int(mass)}G_PLACEHOLDER", float(CFG["ballast_diameter_mm"]) / 2.0, length, (0, 0, -60), dark, "04_PENDULUM", pendulum_axis, vertices=64, rotation=(0, math.radians(90), 0), bevel=0.5)
        ballast["MATERIAL"] = "steel washers/plates/bar; plastic excluded"
        ballast["MASS_G"] = mass
        ballast["COLLISION_GROUP"] = "PENDULUM_DYNAMIC"
        ballast.hide_render = mass != CFG["ballast_mass_g"]
        ballast.hide_set(mass != CFG["ballast_mass_g"])
        link_to_collection(ballast, "PLACEHOLDERS")

    encoder_magnet = cylinder("PENDULUM_ENCODER_MAGNET_PLACEHOLDER", 4.0, 2.0, (64.5, 0, 0), dark, "04_PENDULUM", pendulum_axis, vertices=32, rotation=(0, math.radians(90), 0), bevel=0.2)
    pend_encoder = box("PENDULUM_ENCODER_SENSOR_PLACEHOLDER", (3, 18, 18), (67, 0, 0), green, "03_STEERING", steering_root, bevel=1.0)
    pend_encoder_guard = drilled_box("PENDULUM_ENCODER_GUARD", (6, 30, 30), (69, 0, 0), [((0, 0, 0), 22.0, (1, 0, 0))], orange, "03_STEERING", steering_root, bevel=2.0)
    print_meta(pend_encoder_guard, orientation="broad face on bed", walls=5, infill=40, supports=False, brim=False, status="BLOCKED", placeholders="encoder sensor and magnet")
    for obj in (encoder_magnet, pend_encoder):
        link_to_collection(obj, "PLACEHOLDERS")

    # Electronics are physically bolted to fixed-frame rings. The known PCB is
    # separate from still-unknown component/connector envelopes.
    pcb = drilled_box("ESP32_P4_M3_PCB", CFG["esp32_p4_m3_pcb_mm"], (0, 0, 92), [((-28.2, -31.0, 0), float(CFG["esp32_mount_hole_diameter_mm_PLACEHOLDER"]), (0, 0, 1)), ((28.2, -31.0, 0), float(CFG["esp32_mount_hole_diameter_mm_PLACEHOLDER"]), (0, 0, 1)), ((-28.2, 31.0, 0), float(CFG["esp32_mount_hole_diameter_mm_PLACEHOLDER"]), (0, 0, 1)), ((28.2, 31.0, 0), float(CFG["esp32_mount_hole_diameter_mm_PLACEHOLDER"]), (0, 0, 1))], green, "05_ELECTRONICS", electronics_root, bevel=0.4)
    pcb["SOURCE"] = "user specified PCB 92x62x1.6 mm; holes remain placeholder"
    pcb["COLLISION_GROUP"] = "FIXED_OBSTACLE"
    pcb_top = box("ESP32_TOP_COMPONENT_ENVELOPE_PLACEHOLDER", (88, 58, float(CFG["esp32_top_envelope_height_mm_PLACEHOLDER"])), (0, 0, 98.8), green, "05_ELECTRONICS", electronics_root, bevel=1.0)
    pcb_bottom = box("ESP32_BOTTOM_COMPONENT_ENVELOPE_PLACEHOLDER", (84, 54, float(CFG["esp32_bottom_envelope_height_mm_PLACEHOLDER"])), (0, 0, 89.2), green, "05_ELECTRONICS", electronics_root, bevel=1.0)
    usb_keepout = box("ESP32_USB_KEEPOUT_PLACEHOLDER", CFG["esp32_usb_keepout_mm_PLACEHOLDER"], (53, 0, 94), yellow, "05_ELECTRONICS", electronics_root, bevel=1.0)
    aux_keepout = box("ESP32_AUX_CONNECTOR_KEEPOUT_PLACEHOLDER", CFG["esp32_aux_connector_keepout_mm_PLACEHOLDER"], (-52, 12, 94), yellow, "05_ELECTRONICS", electronics_root, bevel=1.0)
    for obj in (pcb_top, pcb_bottom, usb_keepout, aux_keepout):
        obj["COLLISION_GROUP"] = "FIXED_OBSTACLE"
        link_to_collection(obj, "PLACEHOLDERS")
    pcb_tray = drilled_box("PCB_TRAY", (104, 74, 4), (0, 0, 85), [((-43, -28, 0), 3.4, (0, 0, 1)), ((43, -28, 0), 3.4, (0, 0, 1)), ((-43, 28, 0), 3.4, (0, 0, 1)), ((43, 28, 0), 3.4, (0, 0, 1))], grey, "05_ELECTRONICS", electronics_root, bevel=2)
    window = box("PCB_TRAY_WINDOW", (82, 52, 8), (0, 0, 85), grey, "00_REFERENCE", bevel=2)
    boolean_difference(pcb_tray, window, "Pendulum clearance and ventilation window")
    print_meta(pcb_tray, orientation="flat on bed", walls=6, infill=40, supports=False, brim=False, status="BLOCKED", placeholders="ESP32 hole pattern and connector keepouts")
    for link_index, (x, y) in enumerate(((-43, -28), (43, -28), (-43, 28), (43, 28)), start=1):
        angle = math.atan2(y, x)
        tray_link = strut_between(f"PCB_TRAY_FRAME_LINK_{link_index:02d}", (x, y, 85), (66 * math.cos(angle), 66 * math.sin(angle), 82), 7.0, grey, "05_ELECTRONICS", electronics_root, export=(link_index == 1), quantity=4)
        tray_link["PRINT_STATUS"] = "BLOCKED"
        fastener_cylinder(f"PCB_TRAY_LINK_M3_{link_index:02d}", 5.5, 6.0, (66 * math.cos(angle), 66 * math.sin(angle), 85), (0, 0, 1), dark, electronics_root, "M3 through bolt into fixed-frame top ring")
    mechanical_connection(pcb_tray, "FIXED_FRAME_TOP", "4x M3 frame-link screws + 4 board standoffs", "four frame links and tray perimeter", "bolt links to top ring, then install PCB", "remove PCB standoffs and four frame-link screws", "2.5 mm hex; USB remains accessible", "four-corner pattern", "four M3 links")

    battery_current = CFG["battery_size_mm_CURRENT_MODEL_PLACEHOLDER"]
    battery_candidate = CFG["battery_size_mm_USER_REPORTED_CANDIDATE"]
    battery = box("BATTERY_CURRENT_MODEL_PLACEHOLDER", battery_current, (0, 0, -98), blue, "05_ELECTRONICS", electronics_root, bevel=4)
    battery_alt = box("BATTERY_USER_REPORTED_CANDIDATE", battery_candidate, (0, 0, -98), blue, "05_ELECTRONICS", electronics_root, bevel=4)
    battery_alt.hide_render = True
    battery["REPLACEABLE"] = True
    for obj in (battery, battery_alt):
        obj["COLLISION_GROUP"] = "FIXED_OBSTACLE"
        link_to_collection(obj, "PLACEHOLDERS")
    battery_tray = drilled_box("BATTERY_TRAY", (88, 54, 3.2), (0, 0, -112), [((-37, -20, 0), 3.4, (0, 0, 1)), ((37, -20, 0), 3.4, (0, 0, 1)), ((-37, 20, 0), 3.4, (0, 0, 1)), ((37, 20, 0), 3.4, (0, 0, 1))], grey, "05_ELECTRONICS", electronics_root, bevel=1.8)
    print_meta(battery_tray, orientation="flat base on bed", walls=7, infill=45, supports=False, brim=False, status="BLOCKED", placeholders="conflicting battery envelopes, BMS and cable exit")
    for y in (-25, 25):
        box(f"BATTERY_TRAY_RAIL_{y}", (88, 4, 21), (0, y, -102), grey, "05_ELECTRONICS", electronics_root, bevel=1.2)
    for x in (-39, 39):
        box(f"BATTERY_END_STOP_{x}", (4, 50, 20), (x, 0, -102), grey, "05_ELECTRONICS", electronics_root, bevel=1.2)
    for x in (-25, 25):
        box(f"BATTERY_STRAP_GUIDE_{x}", (4, 58, 4), (x, 0, -85), grey, "05_ELECTRONICS", electronics_root, bevel=1.0)
    bms_keepout = box("BATTERY_BMS_KEEPOUT_PLACEHOLDER", CFG["battery_bms_keepout_mm_PLACEHOLDER"], (0, 0, -79), yellow, "05_ELECTRONICS", electronics_root, bevel=1.0)
    link_to_collection(bms_keepout, "PLACEHOLDERS")
    for link_index, (x, y) in enumerate(((-38, -20), (38, -20), (-38, 20), (38, 20)), start=1):
        angle = math.atan2(y, x)
        tray_link = strut_between(f"BATTERY_TRAY_FRAME_LINK_{link_index:02d}", (x, y, -112), (66 * math.cos(angle), 66 * math.sin(angle), -82), 7.0, grey, "05_ELECTRONICS", electronics_root, export=(link_index == 1), quantity=4)
        tray_link["PRINT_STATUS"] = "BLOCKED"
        fastener_cylinder(f"BATTERY_TRAY_LINK_M3_{link_index:02d}", 5.5, 6.0, (66 * math.cos(angle), 66 * math.sin(angle), -85), (0, 0, 1), dark, electronics_root, "M3 through bolt into fixed-frame bottom ring")
    mechanical_connection(battery_tray, "FIXED_FRAME_BOTTOM", "4x M3 frame links + two straps", "four diagonal links, end stops and side rails", "bolt links, insert battery through hatch, tension straps", "park pendulum away; release straps and slide through hatch", "2.5 mm hex; fingers through hatch", "four end/side stops", "two straps and four frame links")

    # A fixed IMU cannot reach the 10–25 mm target: the 46 mm ballast holder
    # closes the only yaw gap. This is the nearest serviceable fixed-frame route
    # retained for mesh validation, and is explicitly not called target-compliant.
    imu_center = Vector((75, 0, 35))
    imu = box("IMU_MPU9250_PLACEHOLDER", (4, 20, 15), imu_center, green, "05_ELECTRONICS", electronics_root, bevel=1)
    imu["ORIENTATION"] = "vertical YZ plane; axes marked on mount"
    imu["COLLISION_GROUP"] = "FIXED_OBSTACLE"
    link_to_collection(imu, "PLACEHOLDERS")
    imu_mount = drilled_box("IMU_MOUNT", (3, 28, 23), (80, 0, 35), [((0, -9, -6), 2.6, (1, 0, 0)), ((0, 9, -6), 2.6, (1, 0, 0)), ((0, -9, 6), 2.6, (1, 0, 0)), ((0, 9, 6), 2.6, (1, 0, 0))], grey, "05_ELECTRONICS", electronics_root, bevel=0.6)
    print_meta(imu_mount, orientation="broad face on bed", walls=6, infill=60, supports=False, brim=False, status="BLOCKED", placeholders="actual MPU module holes")
    imu_mount["CENTER_OFFSET_MM"] = round(imu_center.length, 1)
    imu_mount["TARGET_OFFSET_BLOCKER"] = "full 360 ballast envelope closes fixed-frame route to 25 mm target"
    imu_cantilever = strut_between("IMU_FIXED_FRAME_CANTILEVER", (82, 0, 35), (106, 0, 35), 7.0, grey, "05_ELECTRONICS", electronics_root, export=True)
    imu_cantilever["PRINT_STATUS"] = "BLOCKED"
    mechanical_connection(imu_mount, "FIXED_FRAME_RING via IMU_FIXED_FRAME_CANTILEVER", "2x M3 mount screws + 2x cantilever screws", "rigid 3 mm plate and 7 mm cantilever", "install with axis arrow +X/+Y/+Z visible", "remove two sensor screws without shaft removal", "2 mm/2.5 mm hex", "two spaced screws", "cantilever end screws")

    driver = box("MOTOR_DRIVER_PLACEHOLDER", (45, 12, 35), (0, 96, 40), green, "05_ELECTRONICS", electronics_root, bevel=2)
    driver["COLLISION_GROUP"] = "FIXED_OBSTACLE"
    link_to_collection(driver, "PLACEHOLDERS")
    driver_tray = drilled_box("DRIVER_TRAY", (53, 4, 43), (0, 88, 40), [((-20, 0, -15), 3.4, (0, 1, 0)), ((20, 0, -15), 3.4, (0, 1, 0)), ((-20, 0, 15), 3.4, (0, 1, 0)), ((20, 0, 15), 3.4, (0, 1, 0))], grey, "05_ELECTRONICS", electronics_root, bevel=1.5)
    print_meta(driver_tray, orientation="broad face on bed", walls=6, infill=45, supports=False, brim=False, status="BLOCKED", placeholders="driver mounting holes, terminals and heatsink")
    for link_index, x in enumerate((-20, 20), start=1):
        driver_link = strut_between(f"DRIVER_TRAY_FRAME_LINK_{link_index:02d}", (x, 88, 40), (x, 103, 8), 7.0, grey, "05_ELECTRONICS", electronics_root, export=(link_index == 1), quantity=2)
        driver_link["PRINT_STATUS"] = "BLOCKED"
    mechanical_connection(driver_tray, "FIXED_FRAME_RING", "2 frame links + 4 board screws", "two diagonal links and tray plate", "bolt links then board", "remove board screws and two links", "2.5 mm hex", "two links", "four board screws")
    switch_holder = drilled_box("SWITCH_HOLDER", (18, 28, 6), (inner_r - 10, 12, 0), [((0, -9, 0), 3.4, (1, 0, 0)), ((0, 9, 0), 3.4, (1, 0, 0))], grey, "05_ELECTRONICS", electronics_root, bevel=1.0)
    charge_holder = drilled_box("CHARGE_PORT_HOLDER", (18, 22, 6), (inner_r - 10, -12, 0), [((0, -7, 0), 3.4, (1, 0, 0)), ((0, 7, 0), 3.4, (1, 0, 0))], grey, "05_ELECTRONICS", electronics_root, bevel=1.0)
    print_meta(switch_holder, orientation="flat on bed", walls=5, infill=45, supports=False, brim=False, status="BLOCKED", placeholders="switch cutout and panel thickness")
    print_meta(charge_holder, orientation="flat on bed", walls=5, infill=45, supports=False, brim=False, status="BLOCKED", placeholders="charge connector cutout and flange")
    mechanical_connection(switch_holder, "SERVICE_HATCH", "2x M3 screws", "switch flange and holder shoulder", "install from rear of hatch", "remove hatch, then two screws", "2.5 mm hex", "rectangular cutout", "two screws")
    mechanical_connection(charge_holder, "SERVICE_HATCH", "2x M3 screws", "connector flange and holder shoulder", "install from rear of hatch", "remove hatch, then two screws", "2.5 mm hex", "rectangular cutout", "two screws")
    for idx, a in enumerate((25, 55, 125, 155, 205, 235, 305, 335), start=1):
        rad = math.radians(a)
        clip = box(f"CABLE_CLIP_{idx:02d}", (12, 5, 8), (108 * math.cos(rad), 108 * math.sin(rad), 28 if idx % 2 else -28), grey, "05_ELECTRONICS", electronics_root, bevel=1.2)
        clip.rotation_euler.z = rad
        clip["CABLE_ROUTE"] = "fixed shell side only; outside pendulum swept volume"
        if idx == 1:
            print_meta(clip, orientation="flat on bed", walls=4, infill=60, supports=False, brim=False, quantity=8, status="BLOCKED", placeholders="wire diameters")

    power_route = cable_route("POWER_CABLE_ENVELOPE", [(0, 0, -78), (0, 82, -72), (0, 112, -30), (0, 104, 25), (0, 96, 40)], float(CFG["wire_power_envelope_diameter_mm"]), blue, "05_ELECTRONICS", electronics_root)
    sensor_route = cable_route("IMU_SENSOR_CABLE_ENVELOPE", [(75, 0, 35), (106, 0, 35), (112, 20, 55), (75, 55, 82), (40, 30, 92)], float(CFG["wire_sensor_envelope_diameter_mm"]), yellow, "05_ELECTRONICS", electronics_root)
    yaw_flex = cable_route("STEERING_FLEX_LOOP_ENVELOPE", [(0, 104, 25), (18, 104, 15), (24, 98, 5), (14, 94, -5), (0, 94, 0)], float(CFG["wire_power_envelope_diameter_mm"]), blue, "05_ELECTRONICS", electronics_root)
    steering_power = cable_route("STEERING_FRAME_POWER_ROUTE", [(0, 92, 0), (-20, 82, -8), (-55, 58, -14), (-82, 20, -10), (-96, 0, -2)], float(CFG["wire_power_envelope_diameter_mm"]), blue, "03_STEERING", steering_root)
    for route in (power_route, sensor_route, yaw_flex):
        route["ATTACHMENT"] = "fixed-frame cable clips and strain relief"
    steering_power["ATTACHMENT"] = "steering-frame clips; flex loop only at yaw joint"
    strain_a = box("POWER_STRAIN_RELIEF_FIXED", (16, 8, 8), (0, 101, 25), grey, "05_ELECTRONICS", electronics_root, bevel=1.0)
    strain_b = box("POWER_STRAIN_RELIEF_STEERING", (16, 8, 8), (0, 91, 0), orange, "03_STEERING", steering_root, bevel=1.0)

    # Print jigs and fit coupons.
    stand = ring("BALL_STAND", 176, 138, 22, (0, 0, -145), grey, "08_PRINT_JIGS", None, export=True)
    stand["PRINT_ORIENTATION"] = "flat on bed"
    stand["PRINT_STATUS"] = "PRINT_READY"
    balance_side = drilled_box("BALANCE_STAND_SIDE", (18, 150, 120), (210, 0, 0), [((0, 0, 35), 10, (1, 0, 0))], grey, "08_PRINT_JIGS", None, bevel=5)
    print_meta(balance_side, orientation="broad side on bed", walls=6, infill=25, supports=False, brim=True, quantity=2, status="PRINT_READY")
    test_base = drilled_box("PENDULUM_TEST_STAND_BASE", (180, 90, 8), (0, 220, 0), [((-70, -30, 0), 3.4, (0, 0, 1)), ((70, -30, 0), 3.4, (0, 0, 1)), ((-70, 30, 0), 3.4, (0, 0, 1)), ((70, 30, 0), 3.4, (0, 0, 1))], grey, "08_PRINT_JIGS", None, bevel=3)
    print_meta(test_base, orientation="flat on bed", walls=5, infill=25, supports=False, brim=False, status="PRINT_READY")
    test_upright = drilled_box("PENDULUM_TEST_STAND_UPRIGHT", (12, 70, 120), (110, 220, 60), [((0, 0, 40), 22.0, (1, 0, 0)), ((0, -25, -45), 3.4, (1, 0, 0)), ((0, 25, -45), 3.4, (1, 0, 0))], grey, "08_PRINT_JIGS", None, bevel=3)
    print_meta(test_upright, orientation="broad side on bed", walls=6, infill=40, supports=False, brim=True, quantity=2, status="PRINT_READY")
    alignment = arc_bar("SEGMENT_ALIGNMENT_TEMPLATE", outer_r, outer_r - 6, 14, -18, 18, 0, grey, "08_PRINT_JIGS", export=True)
    alignment.location = (-220, 190, 0)
    alignment["PRINT_STATUS"] = "PRINT_READY"

    m3_coupon = drilled_box("M3_TEST_COUPON", (70, 25, 8), (-220, 0, 0), [((-22, 0, 0), 3.2, (0, 0, 1)), ((0, 0, 0), 3.4, (0, 0, 1)), ((22, 0, 0), 3.6, (0, 0, 1))], grey, "08_PRINT_JIGS", None, bevel=2)
    print_meta(m3_coupon, orientation="flat on bed", walls=5, infill=80, supports=False, brim=False, status="PRINT_READY")
    bearing_coupon = drilled_box("BEARING_FIT_COUPON", (85, 34, 10), (-220, -50, 0), [((-27, 0, 0), 21.8, (0, 0, 1)), ((0, 0, 0), 22.0, (0, 0, 1)), ((27, 0, 0), 22.2, (0, 0, 1))], grey, "08_PRINT_JIGS", None, bevel=2)
    print_meta(bearing_coupon, orientation="flat on bed", walls=6, infill=80, supports=False, brim=False, status="PRINT_READY")
    joint_coupon = arc_bar("SPHERICAL_JOINT_TEST_FRAGMENT", outer_r, inner_r, 32, -14, 14, 0, white_solid, "08_PRINT_JIGS", export=True)
    joint_coupon.location = (-220, -110, 0)
    joint_coupon["PRINT_STATUS"] = "PRINT_READY"
    insert_template = drilled_box("HEAT_INSERT_TEMPLATE", (90, 28, 10), (-220, -165, 0), [((-30, 0, 0), 3.8, (0, 0, 1)), ((-10, 0, 0), 4.0, (0, 0, 1)), ((10, 0, 0), 4.2, (0, 0, 1)), ((30, 0, 0), 4.4, (0, 0, 1))], grey, "08_PRINT_JIGS", None, bevel=2)
    print_meta(insert_template, orientation="flat on bed", walls=5, infill=80, supports=False, brim=False, status="PRINT_READY")
    shaft_jig = drilled_box("SHAFT_ALIGNMENT_JIG", (140, 36, 10), (-220, -220, 0), [((-50, 0, 0), 8.2, (0, 0, 1)), ((50, 0, 0), 8.2, (0, 0, 1))], grey, "08_PRINT_JIGS", None, bevel=2.0)
    print_meta(shaft_jig, orientation="flat on bed", walls=6, infill=70, supports=False, brim=False, status="PRINT_READY")
    silicone_template = drilled_box("SILICONE_GRIP_TEMPLATE", (100, 34, 3), (-220, -260, 0), [((-36, 0, 0), 2.8, (0, 0, 1)), ((-12, 0, 0), 2.8, (0, 0, 1)), ((12, 0, 0), 2.8, (0, 0, 1)), ((36, 0, 0), 2.8, (0, 0, 1))], grey, "08_PRINT_JIGS", None, bevel=1.0)
    print_meta(silicone_template, orientation="flat on bed", walls=4, infill=40, supports=False, brim=False, status="PRINT_READY")

    swept, arm_env = collision_sweep_v2(inner_r, steering_root, yellow)
    status_text = add_text("COLLISION_STATUS", "MESH COLLISION CHECK: PENDING", (0, -150, 150), 10, yellow, "09_COLLISION_ENVELOPES")
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

    source_report = validate_export_meshes()
    if not source_report["all_manifold"]:
        failed = [name for name, row in source_report["objects"].items() if not row["valid"]]
        details = {name: source_report["objects"][name] for name in failed}
        raise RuntimeError(f"Source mesh validation failed without repair: {details}")

    export_spec = importlib.util.spec_from_file_location("export_parts", HERE / "export_parts.py")
    export_module = importlib.util.module_from_spec(export_spec)
    export_spec.loader.exec_module(export_module)
    prepared = export_module.prepare_export_duplicates()

    validation_spec = importlib.util.spec_from_file_location("validate_robot", HERE / "validate_robot.py")
    validation_module = importlib.util.module_from_spec(validation_spec)
    sys.modules[validation_spec.name] = validation_module
    validation_spec.loader.exec_module(validation_module)
    collision_report = validation_module.validate_scene(ROOT)
    manifest = export_module.main(prepared)
    report = {
        "status": collision_report["status"],
        "project_revision": CFG["project_revision"],
        "source_meshes": source_report,
        "collision_report": "collision_report.json",
        "print_manifest": "print_manifest.json",
        "exported_stl_count": len(manifest),
        "print_ready_count": sum(1 for row in manifest if row["status"] == "PRINT_READY"),
        "minimum_dynamic_clearance_mm": collision_report["minimum_clearance_mm"],
    }
    (ROOT / "exports" / "validation_report.json").write_text(json.dumps(report, indent=2) + "\n")
    status_text.data.body = f"MESH COLLISION: {collision_report['status']} / {collision_report['minimum_clearance_mm']} mm"
    status_text.hide_render = False

    create_renders(panel_objects, prepared)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    print(f"BUILD COMPLETE: {BLEND_PATH}")
    print(f"Collision status: {scene['collision_status']}; minimum clearance {scene['collision_min_clearance_mm']} mm")
    print(f"Printable parts: {len(manifest)}; PRINT_READY: {report['print_ready_count']}; topology: PASS")


if __name__ == "__main__":
    build()
