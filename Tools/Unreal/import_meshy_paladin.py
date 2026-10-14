"""Importa en Unreal la version detallada del Paladin del Ocaso generada en Meshy."""

from pathlib import Path

import unreal


PROJECT_ROOT = Path(r"C:\Users\isaac\Documents\Proyectos\Ten Fe")
SOURCE_FBX = (
    PROJECT_ROOT
    / "Assets"
    / "Characters"
    / "Enemies"
    / "Paladin"
    / "Exports"
    / "SM_PaladinSoldier_Meshy.fbx"
)
DESTINATION = "/Game/Characters/Enemies/Paladin"
ASSET_NAME = "SM_PaladinSoldier_Meshy"
ASSET_PATH = f"{DESTINATION}/{ASSET_NAME}.{ASSET_NAME}"
TEXTURE_ROOT = SOURCE_FBX.parent.parent / "Textures" / "Meshy"
TEXTURES = {
    "base_color": TEXTURE_ROOT / "T_Paladin_Meshy_BaseColor.png",
    "orm": TEXTURE_ROOT / "T_Paladin_Meshy_ORM.png",
    "normal": TEXTURE_ROOT / "T_Paladin_Meshy_Normal.png",
}


if not SOURCE_FBX.is_file():
    raise RuntimeError(f"No se encontro el FBX preparado: {SOURCE_FBX}")

options = unreal.FbxImportUI()
options.import_mesh = True
options.import_as_skeletal = False
options.import_materials = True
options.import_textures = False
options.static_mesh_import_data.combine_meshes = True
options.static_mesh_import_data.generate_lightmap_u_vs = True
options.static_mesh_import_data.auto_generate_collision = False
options.static_mesh_import_data.convert_scene = True
options.static_mesh_import_data.convert_scene_unit = True
try:
    options.static_mesh_import_data.build_nanite = True
except Exception:
    unreal.log_warning("TENFE_PALADIN: build_nanite no esta disponible en FbxImportUI")

task = unreal.AssetImportTask()
task.filename = str(SOURCE_FBX)
task.destination_path = DESTINATION
task.destination_name = ASSET_NAME
task.automated = True
task.replace_existing = True
task.replace_existing_settings = True
task.save = True
task.options = options

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

texture_tasks = []
for texture_path in TEXTURES.values():
    if not texture_path.is_file():
        raise RuntimeError(f"No se encontro la textura preparada: {texture_path}")
    texture_task = unreal.AssetImportTask()
    texture_task.filename = str(texture_path)
    texture_task.destination_path = DESTINATION
    texture_task.destination_name = texture_path.stem
    texture_task.automated = True
    texture_task.replace_existing = True
    texture_task.replace_existing_settings = True
    texture_task.save = True
    texture_tasks.append(texture_task)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(texture_tasks)

if not unreal.EditorAssetLibrary.does_asset_exist(ASSET_PATH):
    raise RuntimeError(f"Unreal no creo la malla esperada: {ASSET_PATH}")

mesh = unreal.load_asset(ASSET_PATH)
if not mesh:
    raise RuntimeError(f"No se pudo cargar la malla importada: {ASSET_PATH}")

nanite_enabled = False
try:
    nanite_settings = mesh.get_editor_property("nanite_settings")
    nanite_settings.enabled = True
    mesh.set_editor_property("nanite_settings", nanite_settings)
    nanite_enabled = True
except Exception as error:
    unreal.log_warning(f"TENFE_PALADIN: no se pudo activar Nanite: {error}")

texture_assets = {}
for role, source_path in TEXTURES.items():
    texture_asset_path = f"{DESTINATION}/{source_path.stem}.{source_path.stem}"
    texture = unreal.load_asset(texture_asset_path)
    if not texture:
        raise RuntimeError(f"No se pudo cargar la textura importada: {texture_asset_path}")
    texture_assets[role] = texture

texture_assets["base_color"].set_editor_property("srgb", True)
texture_assets["orm"].set_editor_property("srgb", False)
texture_assets["orm"].set_editor_property(
    "compression_settings", unreal.TextureCompressionSettings.TC_MASKS
)
texture_assets["normal"].set_editor_property("srgb", False)
texture_assets["normal"].set_editor_property(
    "compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP
)

material_path = f"{DESTINATION}/M_Paladin_Meshy_PBR.M_Paladin_Meshy_PBR"
material = unreal.load_asset(material_path)
if not material:
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "M_Paladin_Meshy_PBR", DESTINATION, unreal.Material, unreal.MaterialFactoryNew()
    )
if not material:
    raise RuntimeError("No se pudo crear M_Paladin_Meshy_PBR")

unreal.MaterialEditingLibrary.delete_all_material_expressions(material)
base_node = unreal.MaterialEditingLibrary.create_material_expression(
    material, unreal.MaterialExpressionTextureSample, -620, -180
)
base_node.set_editor_property("texture", texture_assets["base_color"])
orm_node = unreal.MaterialEditingLibrary.create_material_expression(
    material, unreal.MaterialExpressionTextureSample, -620, 20
)
orm_node.set_editor_property("texture", texture_assets["orm"])
orm_node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
normal_node = unreal.MaterialEditingLibrary.create_material_expression(
    material, unreal.MaterialExpressionTextureSample, -620, 220
)
normal_node.set_editor_property("texture", texture_assets["normal"])
normal_node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)

unreal.MaterialEditingLibrary.connect_material_property(
    base_node, "RGB", unreal.MaterialProperty.MP_BASE_COLOR
)
unreal.MaterialEditingLibrary.connect_material_property(
    orm_node, "G", unreal.MaterialProperty.MP_ROUGHNESS
)
unreal.MaterialEditingLibrary.connect_material_property(
    orm_node, "B", unreal.MaterialProperty.MP_METALLIC
)
unreal.MaterialEditingLibrary.connect_material_property(
    normal_node, "RGB", unreal.MaterialProperty.MP_NORMAL
)
unreal.MaterialEditingLibrary.recompile_material(material)
mesh.set_material(0, material)

materials = mesh.get_editor_property("static_materials")
material_names = [
    slot.get_editor_property("material_interface").get_name()
    if slot.get_editor_property("material_interface")
    else "None"
    for slot in materials
]

unreal.EditorAssetLibrary.save_directory(DESTINATION, only_if_is_dirty=False, recursive=True)
unreal.log(
    "TENFE_MESHY_PALADIN_IMPORTED="
    f"{mesh.get_path_name()};materials={','.join(material_names)};nanite={nanite_enabled}"
)
