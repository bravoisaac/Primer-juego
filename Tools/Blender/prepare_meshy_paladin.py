"""Prepara y valida el paladin generado por Meshy para Ten Fe.

El script conserva el GLB original, normaliza la malla a dos metros, crea una
escena Blender editable, exporta un FBX con texturas incrustadas y genera una
vista previa y un informe JSON reproducible.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\isaac\Documents\Proyectos\Ten Fe")
ASSET_ROOT = PROJECT_ROOT / "Assets" / "Characters" / "Enemies" / "Paladin"
SOURCE_GLB = ASSET_ROOT / "Source" / "PaladinSoldier_Meshy_Source.glb"
BLEND_FILE = ASSET_ROOT / "Source" / "PaladinSoldier_Meshy.blend"
EXPORT_FBX = ASSET_ROOT / "Exports" / "SM_PaladinSoldier_Meshy.fbx"
PREVIEW_FILE = ASSET_ROOT / "Preview" / "PaladinSoldier_Meshy.png"
REPORT_FILE = ASSET_ROOT / "validation_meshy.json"
TEXTURE_DIR = ASSET_ROOT / "Textures" / "Meshy"
TARGET_HEIGHT_METERS = 2.0


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def mesh_objects() -> list[bpy.types.Object]:
    return [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]


def world_bounds(objects: list[bpy.types.Object]) -> tuple[list[float], list[float]]:
    corners = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    if not corners:
        raise RuntimeError("El archivo no contiene geometria de malla")
    minimum = [min(point[index] for point in corners) for index in range(3)]
    maximum = [max(point[index] for point in corners) for index in range(3)]
    return minimum, maximum


def dimensions_from_bounds(minimum: list[float], maximum: list[float]) -> list[float]:
    return [maximum[index] - minimum[index] for index in range(3)]


def triangle_count(objects: list[bpy.types.Object]) -> int:
    total = 0
    for obj in objects:
        obj.data.calc_loop_triangles()
        total += len(obj.data.loop_triangles)
    return total


def collect_stats(objects: list[bpy.types.Object]) -> dict:
    minimum, maximum = world_bounds(objects)
    dimensions = dimensions_from_bounds(minimum, maximum)
    materials = sorted(
        {
            slot.material.name
            for obj in objects
            for slot in obj.material_slots
            if slot.material is not None
        }
    )
    images = sorted(
        image.name
        for image in bpy.data.images
        if image.name not in {"Render Result", "Viewer Node"}
    )
    armatures = [obj.name for obj in bpy.context.scene.objects if obj.type == "ARMATURE"]
    return {
        "mesh_count": len(objects),
        "material_count": len(materials),
        "materials": materials,
        "image_count": len(images),
        "images": images,
        "vertices": sum(len(obj.data.vertices) for obj in objects),
        "polygons": sum(len(obj.data.polygons) for obj in objects),
        "triangles": triangle_count(objects),
        "armatures": armatures,
        "animation_count": len(bpy.data.actions),
        "bounds_meters": {
            "minimum": [round(value, 4) for value in minimum],
            "maximum": [round(value, 4) for value in maximum],
            "dimensions": [round(value, 4) for value in dimensions],
        },
    }


def rename_pbr_assets(objects: list[bpy.types.Object]) -> None:
    """Da nombres estables a material y mapas PBR embebidos por Meshy."""
    materials = {
        slot.material
        for obj in objects
        for slot in obj.material_slots
        if slot.material is not None
    }
    for material in materials:
        material.name = "M_Paladin_Meshy"
        if not material.use_nodes or material.node_tree is None:
            continue
        for node in material.node_tree.nodes:
            if node.type != "TEX_IMAGE" or node.image is None:
                continue
            linked_inputs = {
                link.to_socket.name
                for output in node.outputs
                for link in output.links
            }
            linked_nodes = {
                link.to_node.type
                for output in node.outputs
                for link in output.links
            }
            if "Base Color" in linked_inputs:
                node.image.name = "T_Paladin_Meshy_BaseColor"
            elif "SEPARATE_COLOR" in linked_nodes:
                node.image.name = "T_Paladin_Meshy_ORM"
            elif "NORMAL_MAP" in linked_nodes:
                node.image.name = "T_Paladin_Meshy_Normal"


def save_pbr_images() -> list[str]:
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    saved_paths = []
    for image_name in (
        "T_Paladin_Meshy_BaseColor",
        "T_Paladin_Meshy_ORM",
        "T_Paladin_Meshy_Normal",
    ):
        image = bpy.data.images.get(image_name)
        if image is None:
            raise RuntimeError(f"Falta el mapa PBR esperado: {image_name}")
        output_path = TEXTURE_DIR / f"{image_name}.png"
        image.filepath_raw = str(output_path)
        image.file_format = "PNG"
        image.save()
        saved_paths.append(str(output_path))
    return saved_paths


def normalize_model(objects: list[bpy.types.Object]) -> None:
    minimum, maximum = world_bounds(objects)
    dimensions = dimensions_from_bounds(minimum, maximum)
    if dimensions[2] <= 0.0:
        raise RuntimeError("La altura del modelo no es valida")

    scale_factor = TARGET_HEIGHT_METERS / dimensions[2]
    for obj in objects:
        obj.scale *= scale_factor

    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    minimum, maximum = world_bounds(objects)
    center_x = (minimum[0] + maximum[0]) * 0.5
    center_y = (minimum[1] + maximum[1]) * 0.5
    offset = Vector((-center_x, -center_y, -minimum[2]))
    for obj in objects:
        obj.location += offset

    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)


def join_static_meshes(objects: list[bpy.types.Object]) -> bpy.types.Object:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    if len(objects) > 1:
        bpy.ops.object.join()
    result = bpy.context.view_layer.objects.active
    result.name = "SM_PaladinSoldier_Meshy"
    result.data.name = "SM_PaladinSoldier_Meshy"
    result["tenfe_asset"] = "PaladinSoldier_Meshy"
    result["source_license"] = "CC BY 4.0"
    return result


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def create_preview(model: bpy.types.Object) -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 768
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(PREVIEW_FILE)
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.look = "AgX - Medium High Contrast"

    world = scene.world or bpy.data.worlds.new("TenFePreviewWorld")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.018, 0.022, 0.03, 1.0)
    background.inputs["Strength"].default_value = 0.28

    bpy.ops.object.camera_add(location=(2.1, -3.3, 2.15))
    camera = bpy.context.object
    camera.name = "PreviewCamera"
    camera.data.lens = 58
    look_at(camera, Vector((0.0, 0.0, 1.03)))
    scene.camera = camera

    light_specs = (
        ("Key", (3.0, -3.8, 4.2), 1050.0, (1.0, 0.78, 0.57)),
        ("Fill", (-3.0, -1.5, 2.7), 700.0, (0.55, 0.68, 1.0)),
        ("Rim", (0.8, 3.2, 3.4), 1250.0, (0.65, 0.78, 1.0)),
    )
    for name, location, energy, color in light_specs:
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = f"Preview{name}"
        light.data.energy = energy
        light.data.color = color
        light.data.shape = "DISK"
        light.data.size = 3.0
        look_at(light, Vector((0.0, 0.0, 1.0)))

    bpy.ops.mesh.primitive_plane_add(size=12.0, location=(0.0, 0.0, -0.012))
    floor = bpy.context.object
    floor.name = "PreviewFloor"
    floor_material = bpy.data.materials.new("M_PreviewFloor")
    floor_material.diffuse_color = (0.025, 0.03, 0.04, 1.0)
    floor.data.materials.append(floor_material)

    model.select_set(False)
    PREVIEW_FILE.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    if not SOURCE_GLB.is_file():
        raise RuntimeError(f"No se encontro el GLB fuente: {SOURCE_GLB}")

    EXPORT_FBX.parent.mkdir(parents=True, exist_ok=True)
    BLEND_FILE.parent.mkdir(parents=True, exist_ok=True)
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(SOURCE_GLB))
    imported_meshes = mesh_objects()
    if not imported_meshes:
        raise RuntimeError("Meshy GLB no contiene mallas")

    rename_pbr_assets(imported_meshes)
    texture_paths = save_pbr_images()
    source_stats = collect_stats(imported_meshes)
    if source_stats["armatures"]:
        raise RuntimeError("El GLB contiene un rig; se requiere una preparacion esqueletica separada")

    normalize_model(imported_meshes)
    model = join_static_meshes(imported_meshes)
    prepared_stats = collect_stats([model])

    bpy.ops.object.select_all(action="DESELECT")
    model.select_set(True)
    bpy.context.view_layer.objects.active = model
    bpy.ops.export_scene.fbx(
        filepath=str(EXPORT_FBX),
        use_selection=True,
        object_types={"MESH"},
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="-Y",
        axis_up="Z",
        path_mode="COPY",
        embed_textures=True,
        bake_anim=False,
        add_leaf_bones=False,
    )

    create_preview(model)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_FILE))

    report = {
        "version": 3,
        "asset": "PaladinSoldier_Meshy",
        "generator": "Meshy 6 Lite - Image to 3D",
        "license": "CC BY 4.0",
        "source_glb": str(SOURCE_GLB),
        "blend": str(BLEND_FILE),
        "fbx": str(EXPORT_FBX),
        "preview": str(PREVIEW_FILE),
        "textures": texture_paths,
        "source": source_stats,
        "prepared": prepared_stats,
        "status": "valid",
        "limitations": [
            "Malla estatica sin rig ni animaciones",
            "Generacion a partir de una sola vista frontal",
            "Requiere retopologia antes de usar como personaje animado definitivo",
        ],
    }
    REPORT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("TENFE_MESHY_PALADIN=" + json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
