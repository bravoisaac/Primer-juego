"""Importa el FBX validado del Paladín del Ocaso en el proyecto Unreal."""

from pathlib import Path
import unreal


PROJECT_ROOT = Path(r"C:\Users\isaac\Documents\Proyectos\Ten Fe")
EXPORT_ROOT = PROJECT_ROOT / "Assets" / "Characters" / "Enemies" / "Paladin" / "Exports"
DESTINATION = "/Game/Characters/Enemies/Paladin"
ASSETS = (
    ("SM_PaladinSoldier_RefV2", EXPORT_ROOT / "SM_PaladinSoldier.fbx"),
    ("SM_PaladinGreatsword", EXPORT_ROOT / "SM_PaladinGreatsword.fbx"),
)


tasks = []
for asset_name, source_fbx in ASSETS:
    if not source_fbx.is_file():
        raise RuntimeError(f"No se encontró el FBX: {source_fbx}")
    options = unreal.FbxImportUI()
    options.import_mesh = True
    options.import_as_skeletal = False
    options.import_materials = True
    options.import_textures = False
    options.static_mesh_import_data.combine_meshes = True
    options.static_mesh_import_data.generate_lightmap_u_vs = True
    options.static_mesh_import_data.auto_generate_collision = True
    options.static_mesh_import_data.convert_scene = True
    options.static_mesh_import_data.convert_scene_unit = True

    task = unreal.AssetImportTask()
    task.filename = str(source_fbx)
    task.destination_path = DESTINATION
    task.destination_name = asset_name
    task.automated = True
    task.replace_existing = True
    task.replace_existing_settings = True
    task.save = True
    task.options = options
    tasks.append(task)

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)

for asset_name, _source_fbx in ASSETS:
    expected_path = f"{DESTINATION}/{asset_name}.{asset_name}"
    if not unreal.EditorAssetLibrary.does_asset_exist(expected_path):
        raise RuntimeError(f"Unreal no creó la malla esperada: {expected_path}")
    asset = unreal.load_asset(expected_path)
    unreal.log(f"TENFE_PALADIN_IMPORTED={asset.get_path_name()}")

unreal.EditorAssetLibrary.save_directory(DESTINATION, only_if_is_dirty=False, recursive=True)
