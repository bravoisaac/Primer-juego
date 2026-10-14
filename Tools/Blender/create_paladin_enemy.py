"""Genera el enemigo original Paladin del Ocaso para Ten Fe.

Uso:
    blender --background --python Tools/Blender/create_paladin_enemy.py

El modelo está construido en centímetros, listo para una importación estática en
Unreal Engine. No usa texturas ni recursos externos.
"""

from pathlib import Path
import math

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\isaac\Documents\Proyectos\Ten Fe")
ASSET_ROOT = PROJECT_ROOT / "Assets" / "Characters" / "Enemies" / "Paladin"
SOURCE_FILE = ASSET_ROOT / "Source" / "PaladinSoldier.blend"
EXPORT_FILE = ASSET_ROOT / "Exports" / "SM_PaladinSoldier.fbx"
PREVIEW_FILE = ASSET_ROOT / "Preview" / "PaladinSoldier.png"

MODEL_OBJECTS = []


def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                       bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (*color, 1.0)
    principled.inputs["Metallic"].default_value = metallic
    principled.inputs["Roughness"].default_value = roughness
    return mat


def finish_object(obj, mat, bevel=0.0, smooth=False, model=True):
    if mat:
        obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        mod = obj.modifiers.new("Bordes forjados", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    if smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True
    obj.select_set(False)
    if model:
        MODEL_OBJECTS.append(obj)
    return obj


def cube(name, location, dimensions, mat, bevel=1.0, rotation=(0, 0, 0), model=True):
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    return finish_object(obj, mat, bevel, model=model)


def cylinder(name, location, radius, depth, mat, vertices=12, bevel=0.8,
             rotation=(0, 0, 0), model=True):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth,
        location=location, rotation=rotation
    )
    obj = bpy.context.object
    obj.name = name
    return finish_object(obj, mat, bevel, smooth=True, model=model)


def sphere(name, location, scale, mat, segments=20, rings=12, model=True):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments, ring_count=rings, location=location
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    return finish_object(obj, mat, 0.4, smooth=True, model=model)


def cone(name, location, radius1, radius2, depth, mat, vertices=12,
         rotation=(0, 0, 0), bevel=0.7, model=True):
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices, radius1=radius1, radius2=radius2, depth=depth,
        location=location, rotation=rotation
    )
    obj = bpy.context.object
    obj.name = name
    return finish_object(obj, mat, bevel, smooth=True, model=model)


def extruded_silhouette(name, points_xz, depth, y_center, mat, bevel=0.7, model=True):
    half = depth / 2.0
    count = len(points_xz)
    vertices = [(x, y_center - half, z) for x, z in points_xz]
    vertices += [(x, y_center + half, z) for x, z in points_xz]
    faces = []
    # Frente y reverso.
    faces.append(tuple(range(count)))
    faces.append(tuple(range(count, count * 2))[::-1])
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, next_index, count + next_index, count + index))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return finish_object(obj, mat, bevel, model=model)


def add_sun_emblem(center_x, front_y, center_z, gold):
    cylinder(
        "Escudo_Emblema_Sol", (center_x, front_y, center_z), 9.0, 1.8, gold,
        vertices=20, bevel=0.3, rotation=(math.radians(90), 0, 0)
    )
    for index in range(8):
        angle = math.radians(index * 45)
        x = center_x + math.cos(angle) * 13.0
        z = center_z + math.sin(angle) * 13.0
        ray = cube(
            f"Escudo_Rayo_{index:02d}", (x, front_y, z), (10.0, 1.7, 2.4), gold,
            bevel=0.4, rotation=(0, math.radians(-index * 45), 0)
        )
        # La rotación Y orienta cada rayo en el plano X/Z.
        ray.rotation_euler.y = -angle


def build_paladin():
    steel = material("M_Acero_Oscuro", (0.07, 0.085, 0.10), metallic=0.9, roughness=0.27)
    steel_light = material("M_Acero_Pulido", (0.18, 0.21, 0.24), metallic=0.92, roughness=0.22)
    gold = material("M_Oro_Envejecido", (0.36, 0.21, 0.055), metallic=0.85, roughness=0.34)
    crimson = material("M_Tela_Carmesi", (0.22, 0.018, 0.026), metallic=0.0, roughness=0.78)
    leather = material("M_Cuero_Negro", (0.025, 0.018, 0.014), metallic=0.0, roughness=0.83)
    void = material("M_Ranura_Yelmo", (0.003, 0.003, 0.005), metallic=0.0, roughness=1.0)

    # Piernas y botas.
    for side, x in (("I", -16.0), ("D", 16.0)):
        cube(f"Bota_{side}", (x, -4.0, 9.0), (24.0, 39.0, 18.0), leather, 2.5)
        cylinder(f"Greba_{side}", (x, 0.0, 37.0), 11.5, 43.0, steel, vertices=10, bevel=1.2)
        sphere(f"Rodillera_{side}", (x, -7.0, 61.0), (13.0, 10.0, 9.0), steel_light)
        cylinder(f"Muslo_{side}", (x, 1.0, 81.0), 13.0, 35.0, steel, vertices=10, bevel=1.1)
        cube(f"Faja_Muslo_{side}", (x, 0.0, 94.0), (27.0, 28.0, 5.0), gold, 1.2)

    # Cintura, faldón y torso.
    cube("Pelvis_Armadura", (0.0, 0.0, 99.0), (48.0, 31.0, 24.0), steel, 3.0)
    cube("Cinturon", (0.0, -1.0, 107.0), (58.0, 34.0, 8.0), leather, 1.5)
    cylinder("Hebilla_Solar", (0.0, -19.0, 107.0), 6.0, 3.0, gold, vertices=16,
             bevel=0.5, rotation=(math.radians(90), 0, 0))
    extruded_silhouette(
        "Tabardo_Frontal",
        [(-17, 106), (17, 106), (14, 62), (0, 54), (-14, 62)],
        3.5, -18.5, crimson, 0.8
    )
    extruded_silhouette(
        "Peto_Principal",
        [(-34, 108), (34, 108), (31, 153), (22, 162), (-22, 162), (-31, 153)],
        34.0, 0.0, steel, 2.5
    )
    cube("Peto_Borde_Superior", (0.0, -18.2, 153.0), (54.0, 3.5, 5.0), gold, 1.0)
    cube("Peto_Borde_Central", (0.0, -18.3, 131.0), (5.0, 3.0, 39.0), gold, 0.8)
    cylinder("Peto_Sello_Solar", (0.0, -20.5, 139.0), 8.0, 2.6, gold, vertices=20,
             bevel=0.5, rotation=(math.radians(90), 0, 0))

    # Brazos, hombreras y guanteletes en pose de guardia relajada.
    for side, x, arm_tilt in (("I", -43.0, -0.10), ("D", 43.0, 0.10)):
        sphere(f"Hombrera_{side}", (x, 0.0, 148.0), (19.5, 19.0, 14.0), steel_light)
        cube(f"Hombrera_Borde_{side}", (x, -17.0, 147.0), (37.0, 4.0, 7.0), gold, 1.0)
        cylinder(f"Brazo_Superior_{side}", (x, 0.0, 125.0), 9.5, 37.0, steel,
                 vertices=10, bevel=1.0, rotation=(0, arm_tilt, 0))
        sphere(f"Codo_{side}", (x, -4.0, 107.0), (10.5, 9.0, 9.0), steel_light)
        cylinder(f"Antebrazo_{side}", (x, -1.0, 91.0), 10.0, 30.0, steel_light,
                 vertices=10, bevel=1.0, rotation=(0, -arm_tilt, 0))
        cube(f"Guantelete_{side}", (x, -3.0, 73.0), (19.0, 20.0, 17.0), steel, 2.0)

    # Cuello y gran yelmo cerrado.
    cylinder("Gorjal", (0.0, 0.0, 160.0), 18.5, 13.0, gold, vertices=12, bevel=1.0)
    cylinder("Yelmo", (0.0, 0.0, 178.0), 22.0, 35.0, steel_light, vertices=12, bevel=1.4)
    cone("Yelmo_Corona", (0.0, 0.0, 199.0), 20.0, 8.0, 17.0, steel, vertices=12, bevel=1.0)
    cube("Yelmo_Visera", (0.0, -22.0, 179.0), (42.0, 5.0, 13.0), steel, 1.2)
    cube("Yelmo_Ranura", (0.0, -25.0, 181.0), (29.0, 1.8, 3.0), void, 0.3)
    cube("Yelmo_Nasal", (0.0, -25.8, 173.0), (4.2, 2.0, 19.0), gold, 0.5)
    cube("Yelmo_Cresta", (0.0, 0.0, 211.0), (5.0, 34.0, 18.0), gold, 1.0)

    # Capa asimétrica: silueta original, no replica un personaje existente.
    extruded_silhouette(
        "Capa_Carmesi",
        [(-34, 151), (34, 151), (41, 89), (25, 48), (2, 58), (-17, 45), (-39, 82)],
        4.0, 20.0, crimson, 1.1
    )
    cube("Broche_Capa_I", (-24.0, -17.5, 153.0), (8.0, 3.0, 8.0), gold, 1.3)
    cube("Broche_Capa_D", (24.0, -17.5, 153.0), (8.0, 3.0, 8.0), gold, 1.3)

    # Escudo cometa en la mano izquierda.
    shield_x = -58.0
    extruded_silhouette(
        "Escudo_Cometa",
        [(shield_x - 27, 139), (shield_x + 27, 139),
         (shield_x + 24, 94), (shield_x, 60), (shield_x - 24, 94)],
        8.0, -22.0, steel, 1.6
    )
    extruded_silhouette(
        "Escudo_Borde_Dorado",
        [(shield_x - 24, 136), (shield_x + 24, 136),
         (shield_x + 21, 96), (shield_x, 65), (shield_x - 21, 96)],
        1.8, -26.5, gold, 1.1
    )
    extruded_silhouette(
        "Escudo_Panel",
        [(shield_x - 19, 131), (shield_x + 19, 131),
         (shield_x + 17, 98), (shield_x, 72), (shield_x - 17, 98)],
        2.0, -28.0, crimson, 0.8
    )
    add_sun_emblem(shield_x, -29.5, 108.0, gold)

    # Espada bastarda en la mano derecha.
    sword_x = 58.0
    cube("Espada_Hoja", (sword_x, -2.0, 137.0), (7.0, 2.7, 88.0), steel_light, 0.7)
    cone("Espada_Punta", (sword_x, -2.0, 187.0), 4.0, 0.0, 12.0, steel_light,
         vertices=4, bevel=0.25)
    cube("Espada_Canal", (sword_x, -3.7, 136.0), (1.4, 0.8, 69.0), steel, 0.25)
    cube("Espada_Guarda", (sword_x, -2.0, 91.0), (34.0, 6.0, 6.0), gold, 1.2)
    cylinder("Espada_Empunadura", (sword_x, -2.0, 77.0), 4.2, 22.0, leather,
             vertices=10, bevel=0.6)
    sphere("Espada_Pomo", (sword_x, -2.0, 63.0), (6.5, 6.5, 6.5), gold)

    # Marcas visuales de desgaste mediante remaches y placas desiguales.
    for x, z in ((-22, 120), (22, 120), (-25, 143), (25, 143)):
        cylinder(f"Remache_{x}_{z}", (x, -20.0, z), 2.1, 1.5, gold, vertices=10,
                 bevel=0.25, rotation=(math.radians(90), 0, 0))

    for obj in MODEL_OBJECTS:
        obj["tenfe_asset"] = "PaladinSoldier"
        obj["tenfe_license"] = "Original project asset"


def add_preview_scene():
    floor_mat = material("M_Suelo_Preview", (0.012, 0.014, 0.018), metallic=0.0, roughness=0.92)
    bpy.ops.mesh.primitive_plane_add(size=700, location=(0, 0, -1))
    floor = bpy.context.object
    floor.name = "Preview_Floor"
    floor.data.materials.append(floor_mat)

    world = bpy.context.scene.world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.004, 0.006, 0.012, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.12

    def area(name, location, energy, color, size):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.color = color
        data.shape = "DISK"
        data.size = size
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        obj.location = location
        point_camera(obj, Vector((0, 0, 105)))
        return obj

    # Las coordenadas se expresan en centímetros; Eevee calcula la caída de luz
    # con las unidades internas, por lo que el visor requiere potencias altas.
    area("Luz_Principal", (-230, -290, 310), 850000, (1.0, 0.64, 0.38), 180)
    area("Luz_Contorno", (220, 100, 250), 950000, (0.25, 0.42, 1.0), 140)
    area("Luz_Frontal", (0, -260, 95), 480000, (0.75, 0.82, 1.0), 110)

    camera_data = bpy.data.cameras.new("Camera_Preview")
    camera = bpy.data.objects.new("Camera_Preview", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = (315, -505, 215)
    camera_data.lens = 58
    point_camera(camera, Vector((0, 0, 102)))
    bpy.context.scene.camera = camera


def point_camera(obj, target):
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def save_and_export():
    SOURCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW_FILE.parent.mkdir(parents=True, exist_ok=True)

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "CENTIMETERS"
    scene.unit_settings.scale_length = 0.01
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 720
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(PREVIEW_FILE)
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.7
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE_FILE))
    bpy.ops.render.render(write_still=True)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in MODEL_OBJECTS:
        obj.hide_render = False
        obj.select_set(True)
    bpy.context.view_layer.objects.active = MODEL_OBJECTS[0]
    bpy.ops.export_scene.fbx(
        filepath=str(EXPORT_FILE),
        use_selection=True,
        object_types={"MESH"},
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        global_scale=1.0,
        axis_forward="-Y",
        axis_up="Z",
        use_mesh_modifiers=True,
        mesh_smooth_type="FACE",
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="AUTO"
    )


def main():
    reset_scene()
    build_paladin()
    add_preview_scene()
    save_and_export()
    print(f"TENFE_PALADIN_BLEND={SOURCE_FILE}")
    print(f"TENFE_PALADIN_FBX={EXPORT_FILE}")
    print(f"TENFE_PALADIN_PREVIEW={PREVIEW_FILE}")
    print(f"TENFE_PALADIN_PARTS={len(MODEL_OBJECTS)}")


if __name__ == "__main__":
    main()
