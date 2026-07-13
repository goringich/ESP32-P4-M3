"""Export all objects tagged EXPORT_PART from the open Blender scene."""

from __future__ import annotations

import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
STL_DIR = ROOT / "exports" / "stl"
GLB_DIR = ROOT / "exports" / "glb"


def deselect() -> None:
    bpy.ops.object.select_all(action="DESELECT")


def export_stl(obj: bpy.types.Object, path: Path) -> None:
    deselect()
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if hasattr(bpy.ops.wm, "stl_export"):
        bpy.ops.wm.stl_export(
            filepath=str(path),
            export_selected_objects=True,
            apply_modifiers=True,
            ascii_format=False,
        )
    else:
        bpy.ops.export_mesh.stl(filepath=str(path), use_selection=True, use_mesh_modifiers=True)


def main() -> None:
    STL_DIR.mkdir(parents=True, exist_ok=True)
    GLB_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    for obj in sorted(bpy.data.objects, key=lambda item: item.name):
        if obj.type != "MESH" or not obj.get("EXPORT_PART"):
            continue
        filename = f"{obj.name}.stl"
        export_stl(obj, STL_DIR / filename)
        manifest.append(
            {
                "object": obj.name,
                "file": f"stl/{filename}",
                "material": obj.get("PRINT_MATERIAL", "PETG"),
                "orientation": obj.get("PRINT_ORIENTATION", "see PRINTING.md"),
                "walls": obj.get("PRINT_WALLS", 5),
                "infill_percent": obj.get("PRINT_INFILL", 35),
                "supports": bool(obj.get("PRINT_SUPPORTS", False)),
                "brim": bool(obj.get("PRINT_BRIM", False)),
                "quantity": obj.get("PRINT_QUANTITY", 1),
            }
        )

    export_collections = {
        "01_SHELL", "02_FIXED_FRAME", "03_STEERING", "04_PENDULUM",
        "05_ELECTRONICS", "06_FASTENERS", "07_GRIP",
    }
    deselect()
    for obj in bpy.data.objects:
        if any(c.name in export_collections for c in obj.users_collection):
            obj.hide_set(False)
            obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_DIR / "spherical_robot_assembly.glb"),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
    )
    (ROOT / "exports" / "print_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    )
    print(f"Exported {len(manifest)} STL files and assembly GLB")


if __name__ == "__main__":
    main()
