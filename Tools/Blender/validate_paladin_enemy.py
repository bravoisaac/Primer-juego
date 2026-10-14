"""Valida las exportaciones FBX del Paladín del Ocaso."""

from pathlib import Path
import json

import bpy
from mathutils import Vector


ROOT = Path(r"C:\Users\isaac\Documents\Proyectos\Ten Fe")
ASSET_ROOT = ROOT / "Assets" / "Characters" / "Enemies" / "Paladin"
REPORT_FILE = ASSET_ROOT / "validation.json"


def validate_fbx(name, path):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(path))
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError(f"{name}: el FBX no contiene mallas")
    corners = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
    minimum = [min(point[index] for point in corners) for index in range(3)]
    maximum = [max(point[index] for point in corners) for index in range(3)]
    dimensions = [maximum[index] - minimum[index] for index in range(3)]
    materials = sorted({slot.material.name for obj in meshes for slot in obj.material_slots if slot.material})
    return {
        "name": name,
        "fbx": str(path),
        "mesh_count": len(meshes),
        "material_count": len(materials),
        "materials": materials,
        "vertices": sum(len(obj.data.vertices) for obj in meshes),
        "polygons": sum(len(obj.data.polygons) for obj in meshes),
        "bounds_meters": {
            "minimum": [round(value, 3) for value in minimum],
            "maximum": [round(value, 3) for value in maximum],
            "dimensions": [round(value, 3) for value in dimensions],
        },
        "status": "valid",
    }


report = {
    "version": 2,
    "reference_source": "Tres imágenes ortográficas proporcionadas por el usuario",
    "assets": [
        validate_fbx("PaladinSoldier", ASSET_ROOT / "Exports" / "SM_PaladinSoldier.fbx"),
        validate_fbx("PaladinGreatsword", ASSET_ROOT / "Exports" / "SM_PaladinGreatsword.fbx"),
    ],
    "status": "valid",
}

REPORT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print("TENFE_PALADIN_VALIDATION=" + json.dumps(report, ensure_ascii=False))
