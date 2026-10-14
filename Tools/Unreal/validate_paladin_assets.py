"""Comprueba que las mallas importadas conservan sus materiales en Unreal."""

import unreal


ASSETS = {
    "/Game/Characters/Enemies/Paladin/SM_PaladinSoldier_RefV2.SM_PaladinSoldier_RefV2": 7,
    "/Game/Characters/Enemies/Paladin/SM_PaladinSoldier_Meshy.SM_PaladinSoldier_Meshy": 1,
    "/Game/Characters/Enemies/Paladin/SM_PaladinGreatsword.SM_PaladinGreatsword": 4,
}

REQUIRED_MESHY_ASSETS = (
    "/Game/Characters/Enemies/Paladin/M_Paladin_Meshy_PBR.M_Paladin_Meshy_PBR",
    "/Game/Characters/Enemies/Paladin/T_Paladin_Meshy_BaseColor.T_Paladin_Meshy_BaseColor",
    "/Game/Characters/Enemies/Paladin/T_Paladin_Meshy_ORM.T_Paladin_Meshy_ORM",
    "/Game/Characters/Enemies/Paladin/T_Paladin_Meshy_Normal.T_Paladin_Meshy_Normal",
)


for path, expected_slots in ASSETS.items():
    asset = unreal.load_asset(path)
    if not asset:
        raise RuntimeError(f"No se pudo cargar {path}")
    slots = asset.get_editor_property("static_materials")
    if len(slots) != expected_slots:
        raise RuntimeError(f"{path}: se esperaban {expected_slots} materiales y existen {len(slots)}")
    names = []
    for slot in slots:
        material = slot.get_editor_property("material_interface")
        if not material:
            raise RuntimeError(f"{path}: el slot {slot.material_slot_name} no tiene material")
        names.append(material.get_name())
    unreal.log(f"TENFE_PALADIN_VALID={path};materials={','.join(names)}")

meshy_mesh = unreal.load_asset(
    "/Game/Characters/Enemies/Paladin/SM_PaladinSoldier_Meshy.SM_PaladinSoldier_Meshy"
)
nanite_settings = meshy_mesh.get_editor_property("nanite_settings")
if not nanite_settings.enabled:
    raise RuntimeError("SM_PaladinSoldier_Meshy debe conservar Nanite activado")

for path in REQUIRED_MESHY_ASSETS:
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        raise RuntimeError(f"Falta el recurso PBR de Meshy: {path}")

unreal.log("TENFE_MESHY_PALADIN_VALID=materials+pbr+nanite")
