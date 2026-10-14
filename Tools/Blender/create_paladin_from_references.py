"""Genera el Paladín del Ocaso v2 a partir de las referencias del usuario.

La salida conserva una pose A relajada, proporciones humanas y piezas separadas
para facilitar un rig posterior. También exporta una espada independiente para que
el componente de arma del enemigo pueda moverla durante el ataque.
"""

from pathlib import Path
import math

import bpy
from mathutils import Vector


ROOT = Path(r"C:\Users\isaac\Documents\Proyectos\Ten Fe")
ASSET_ROOT = ROOT / "Assets" / "Characters" / "Enemies" / "Paladin"
BLEND_FILE = ASSET_ROOT / "Source" / "PaladinSoldier.blend"
BODY_FBX = ASSET_ROOT / "Exports" / "SM_PaladinSoldier.fbx"
SWORD_FBX = ASSET_ROOT / "Exports" / "SM_PaladinGreatsword.fbx"
PREVIEW_FRONT = ASSET_ROOT / "Preview" / "PaladinSoldier.png"
PREVIEW_BACK = ASSET_ROOT / "Preview" / "PaladinSoldier_Back.png"
REFERENCES = [
    ASSET_ROOT / "References" / "paladin_orthographic_tpose.png",
    ASSET_ROOT / "References" / "paladin_orthographic_cloak.png",
    ASSET_ROOT / "References" / "paladin_three_quarter.png",
]

BODY_OBJECTS = []
SWORD_OBJECTS = []


def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)


def make_material(name, color, metallic=0.0, roughness=0.5, wear=False):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    shader = nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    if wear:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 8.0
        noise.inputs["Detail"].default_value = 5.0
        noise.inputs["Roughness"].default_value = 0.7
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.18
        bump.inputs["Distance"].default_value = 0.025
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    return mat


def finish(obj, mat, bevel=0.0, smooth=False, group="body"):
    if mat:
        obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Bordes forjados", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
        modifier.limit_method = "ANGLE"
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    if smooth:
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    obj.select_set(False)
    if group == "body":
        BODY_OBJECTS.append(obj)
    elif group == "sword":
        SWORD_OBJECTS.append(obj)
    return obj


def cube(name, location, dimensions, mat, rotation=(0, 0, 0), bevel=0.008, group="body"):
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    return finish(obj, mat, bevel=bevel, group=group)


def sphere(name, location, scale, mat, segments=24, rings=16, group="body"):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    return finish(obj, mat, bevel=0.002, smooth=True, group=group)


def cylinder(name, location, radius, depth, mat, vertices=16, rotation=(0, 0, 0),
             bevel=0.006, group="body"):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation
    )
    obj = bpy.context.object
    obj.name = name
    return finish(obj, mat, bevel=bevel, smooth=True, group=group)


def cone(name, location, radius1, radius2, depth, mat, vertices=16, rotation=(0, 0, 0),
         bevel=0.006, group="body"):
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices, radius1=radius1, radius2=radius2, depth=depth,
        location=location, rotation=rotation
    )
    obj = bpy.context.object
    obj.name = name
    return finish(obj, mat, bevel=bevel, smooth=True, group=group)


def cylinder_between(name, start, end, radius, mat, vertices=14, bevel=0.005, group="body"):
    start = Vector(start)
    end = Vector(end)
    direction = end - start
    midpoint = (start + end) * 0.5
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=direction.length, location=midpoint
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return finish(obj, mat, bevel=bevel, smooth=True, group=group)


def cone_between(name, start, end, radius_start, radius_end, mat, vertices=14,
                 bevel=0.005, group="body"):
    start = Vector(start)
    end = Vector(end)
    direction = end - start
    midpoint = (start + end) * 0.5
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices, radius1=radius_start, radius2=radius_end,
        depth=direction.length, location=midpoint
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return finish(obj, mat, bevel=bevel, smooth=True, group=group)


def extruded_xz(name, points, depth, y, mat, bevel=0.005, group="body"):
    half = depth * 0.5
    count = len(points)
    vertices = [(x, y - half, z) for x, z in points]
    vertices += [(x, y + half, z) for x, z in points]
    faces = [tuple(range(count))[::-1], tuple(range(count, count * 2))]
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, count + index, count + next_index, next_index))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return finish(obj, mat, bevel=bevel, group=group)


def sabaton(name, x, mat, group="body"):
    """Prisma con punta baja para evitar una bota rectangular."""
    half_width = 0.095
    profile = [(-0.245, 0.035), (0.105, 0.035), (0.095, 0.165),
               (-0.105, 0.135), (-0.245, 0.085)]
    vertices = [(x - half_width, y, z) for y, z in profile]
    vertices += [(x + half_width, y, z) for y, z in profile]
    count = len(profile)
    faces = [tuple(range(count))[::-1], tuple(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return finish(obj, mat, bevel=0.009, group=group)


def curve_trim(name, points, radius, mat, group="body"):
    curve_data = bpy.data.curves.new(f"{name}_Curve", "CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 2
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = 2
    spline = curve_data.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, coordinate in zip(spline.bezier_points, points):
        point.co = coordinate
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.select_set(False)
    if group == "body":
        BODY_OBJECTS.append(obj)
    else:
        SWORD_OBJECTS.append(obj)
    return obj


def add_reference_images():
    reference_collection = bpy.data.collections.new("REFERENCIAS_USUARIO")
    bpy.context.scene.collection.children.link(reference_collection)
    for index, path in enumerate(REFERENCES):
        if not path.is_file():
            continue
        image = bpy.data.images.load(str(path), check_existing=True)
        obj = bpy.data.objects.new(f"Referencia_{index + 1}", None)
        obj.empty_display_type = "IMAGE"
        obj.data = image
        obj.empty_display_size = 2.2
        obj.location = (3.0 + index * 2.4, 1.0, 1.2)
        obj.hide_render = True
        obj["origen"] = "Referencia proporcionada por el usuario"
        reference_collection.objects.link(obj)


def build_body():
    steel = make_material("M_Acero_Desgastado", (0.055, 0.065, 0.078), 0.9, 0.34, wear=True)
    bright = make_material("M_Acero_Bordes", (0.17, 0.16, 0.14), 0.92, 0.28, wear=True)
    bronze = make_material("M_Bronce_Envejecido", (0.13, 0.055, 0.018), 0.78, 0.39, wear=True)
    chain = make_material("M_Cota_Malla", (0.025, 0.029, 0.034), 0.72, 0.48, wear=True)
    cloth = make_material("M_Tela_Marron", (0.042, 0.020, 0.013), 0.0, 0.92, wear=True)
    leather = make_material("M_Cuero_Oscuro", (0.032, 0.018, 0.012), 0.0, 0.8, wear=True)
    void = make_material("M_Interior_Yelmo", (0.002, 0.002, 0.003), 0.0, 1.0)

    # Silueta anatómica y cota de malla bajo las placas.
    sphere("Torso_Cota", (0, 0.015, 1.315), (0.285, 0.18, 0.32), chain)
    sphere("Pelvis_Cota", (0, 0.01, 1.02), (0.24, 0.15, 0.20), chain)
    cylinder("Cuello_Cota", (0, 0, 1.61), 0.105, 0.16, chain, vertices=18)

    leg_data = []
    for side, x in (("I", -0.135), ("D", 0.135)):
        # Botas y sabatones segmentados.
        sabaton(f"Bota_{side}", x, leather)
        for plate_index in range(4):
            y = -0.155 + plate_index * 0.05
            z = 0.135 + plate_index * 0.012
            cube(f"Sabatón_{side}_{plate_index}", (x, y, z),
                 (0.205 - plate_index * 0.008, 0.095, 0.055), steel,
                 rotation=(math.radians(4), 0, 0), bevel=0.009)

        # Greba ahusada y bordes ornamentales.
        cone(f"Greba_{side}", (x, 0, 0.405), 0.105, 0.082, 0.47, steel, vertices=18, bevel=0.008)
        extruded_xz(f"Greba_Frontal_{side}", [
            (x - 0.055, 0.59), (x + 0.055, 0.59), (x + 0.045, 0.27),
            (x, 0.23), (x - 0.045, 0.27)
        ], 0.025, -0.105, bright, bevel=0.007)
        curve_trim(f"Greba_Ornamento_{side}", [
            (x, -0.111, 0.28), (x - 0.035, -0.112, 0.40),
            (x, -0.112, 0.55), (x + 0.035, -0.112, 0.40), (x, -0.112, 0.28)
        ], 0.007, bronze)

        # Rodillera apuntada y protección lateral.
        extruded_xz(
            f"Rodillera_{side}",
            [(x - 0.105, 0.69), (x + 0.105, 0.69), (x + 0.085, 0.59),
             (x, 0.525), (x - 0.085, 0.59)],
            0.11, -0.11, steel, bevel=0.009
        )
        curve_trim(f"Rodillera_Borde_{side}", [
            (x - 0.085, -0.171, 0.67), (x, -0.172, 0.545), (x + 0.085, -0.171, 0.67)
        ], 0.008, bronze)

        # Muslo con cota visible y cuatro placas solapadas.
        cone(f"Muslo_Cota_{side}", (x, 0, 0.84), 0.13, 0.115, 0.40, chain, vertices=18)
        for plate_index in range(4):
            z = 0.76 + plate_index * 0.085
            cone(f"Muslera_{side}_{plate_index}", (x, -0.01, z),
                 0.135, 0.123, 0.105, steel, vertices=18, bevel=0.006)
        leg_data.append((side, x))

    # Faldón, cinturón y placas de cadera inspiradas por las vistas frontal/lateral.
    extruded_xz("Faldón_Frontal", [(-0.145, 1.08), (0.145, 1.08), (0.13, 0.72),
                                     (0.045, 0.63), (-0.055, 0.66), (-0.13, 0.72)],
                0.035, -0.145, cloth, bevel=0.006)
    cube("Cinturón", (0, -0.005, 1.105), (0.52, 0.30, 0.075), leather, bevel=0.012)
    cylinder("Hebilla", (0, -0.177, 1.105), 0.045, 0.022, bronze, vertices=16,
             rotation=(math.radians(90), 0, 0), bevel=0.004)
    for side, sign in (("I", -1), ("D", 1)):
        center = 0.245 * sign
        points = [(center - 0.09, 1.08), (center + 0.09, 1.08),
                  (center + 0.078, 0.76), (center, 0.68), (center - 0.078, 0.76)]
        extruded_xz(f"Escarcela_{side}", points, 0.07, -0.015, steel, bevel=0.009)
        curve_trim(f"Escarcela_Borde_{side}", [
            (center - 0.08, -0.055, 1.055), (center, -0.056, 0.68),
            (center + 0.08, -0.055, 1.055)
        ], 0.007, bronze)

    # Peto anatómico, cresta central y filigrana geométrica.
    sphere("Peto_Volumen", (0, -0.002, 1.32), (0.30, 0.178, 0.30), steel)
    # El volumen principal es curvo; una placa estrecha marca el esternón sin
    # convertir el pecho en una superficie plana tipo escudo.
    extruded_xz("Peto_Placa_Central", [(-0.105, 1.48), (0.105, 1.48),
                                        (0.13, 1.23), (0, 1.065), (-0.13, 1.23)],
                0.022, -0.181, steel, bevel=0.009)
    curve_trim("Peto_Cresta", [
        (0, -0.164, 1.48), (-0.065, -0.167, 1.33), (0, -0.17, 1.12),
        (0.065, -0.167, 1.33), (0, -0.164, 1.48)
    ], 0.012, bright)
    curve_trim("Peto_Filigrana", [
        (-0.19, -0.166, 1.47), (-0.10, -0.17, 1.37), (0, -0.172, 1.31),
        (0.10, -0.17, 1.37), (0.19, -0.166, 1.47)
    ], 0.007, bronze)
    extruded_xz("Peto_Punta", [(-0.08, 1.15), (0, 1.055), (0.08, 1.15), (0, 1.22)],
                0.025, -0.17, bronze, bevel=0.004)

    # Hombreras amplias de tres capas.
    for side, sign in (("I", -1), ("D", 1)):
        shoulder_x = 0.35 * sign
        sphere(f"Hombrera_Base_{side}", (shoulder_x, 0.005, 1.49), (0.19, 0.16, 0.10), steel)
        outer = 0.50
        inner = 0.245
        if sign < 0:
            points = [(-outer, 1.53), (-0.40, 1.59), (-inner, 1.54),
                      (-inner, 1.44), (-0.43, 1.40)]
        else:
            points = [(inner, 1.54), (0.40, 1.59), (outer, 1.53),
                      (0.43, 1.40), (inner, 1.44)]
        extruded_xz(f"Hombrera_Placa_{side}", points, 0.045, -0.165,
                    bright, bevel=0.008)

    # Brazos en pose A relajada y placas solapadas.
    arm_points = {
        "I": [(-0.36, 0, 1.46), (-0.51, 0, 1.25), (-0.59, -0.015, 1.03)],
        "D": [(0.36, 0, 1.46), (0.51, 0, 1.25), (0.59, -0.015, 1.03)],
    }
    for side, (shoulder, elbow, wrist) in arm_points.items():
        sign = -1 if side == "I" else 1
        cylinder_between(f"Brazo_Cota_{side}", shoulder, elbow, 0.082, chain)
        cylinder_between(f"Antebrazo_Cota_{side}", elbow, wrist, 0.073, chain)
        direction = Vector(elbow) - Vector(shoulder)
        for index, t in enumerate((0.24, 0.48, 0.72)):
            center = Vector(shoulder) + direction * t
            cylinder_between(
                f"Brazo_Lámina_{side}_{index}", center - direction.normalized() * 0.055,
                center + direction.normalized() * 0.055, 0.098 - index * 0.006, steel
            )
        cylinder_between(f"Brazal_{side}", elbow, wrist, 0.088, bright, vertices=16)
        sphere(f"Codo_{side}", elbow, (0.095, 0.085, 0.09), steel)
        cube(f"Codo_Espolón_{side}", (elbow[0] + sign * 0.095, -0.005, elbow[2]),
             (0.11, 0.045, 0.045), bronze,
             rotation=(0, math.radians(-28 * sign), 0), bevel=0.006)
        sphere(f"Guantelete_{side}", wrist, (0.085, 0.075, 0.09), steel)
        # Cinco dedos articulados por mano.
        for finger in range(5):
            x_offset = (finger - 2) * 0.014
            start = (wrist[0] + x_offset, -0.035, wrist[2] - 0.055)
            end = (wrist[0] + x_offset + sign * 0.018, -0.055, wrist[2] - 0.145 + abs(finger - 2) * 0.008)
            cylinder_between(f"Dedo_{side}_{finger}", start, end, 0.012, bright, vertices=8, bevel=0.002)

    # Yelmo facetado, visera cerrada y punta piramidal.
    sphere("Cabeza_Interior", (0, 0, 1.74), (0.14, 0.125, 0.18), void)
    cylinder("Yelmo_Casco", (0, 0, 1.76), 0.174, 0.29, steel, vertices=10, bevel=0.008)
    cone("Yelmo_Corona", (0, 0, 1.955), 0.185, 0.0, 0.18, steel, vertices=8, bevel=0.006)
    extruded_xz("Yelmo_Visera", [(-0.17, 1.86), (0.17, 1.86), (0.145, 1.70),
                                  (0, 1.64), (-0.145, 1.70)], 0.055, -0.165, steel, bevel=0.008)
    cube("Yelmo_Ranura", (0, -0.199, 1.80), (0.245, 0.012, 0.025), void, bevel=0.003)
    curve_trim("Yelmo_Borde", [
        (-0.15, -0.198, 1.855), (0, -0.207, 1.885), (0.15, -0.198, 1.855)
    ], 0.008, bronze)
    cube("Yelmo_Nasal", (0, -0.207, 1.725), (0.032, 0.018, 0.17), bronze, bevel=0.004)
    cylinder("Gorjal", (0, 0, 1.58), 0.17, 0.09, bright, vertices=16, bevel=0.006)

    # Capa larga marrón, bufanda y panel posterior ornamentado.
    extruded_xz("Capa", [(-0.34, 1.55), (0.34, 1.55), (0.40, 0.63),
                           (0.29, 0.53), (0.15, 0.58), (0.02, 0.50),
                           (-0.12, 0.58), (-0.27, 0.52), (-0.40, 0.66)],
                0.035, 0.195, cloth, bevel=0.007)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.175, minor_radius=0.045,
                                    major_segments=20, minor_segments=8,
                                    location=(0, 0.015, 1.585))
    scarf = bpy.context.object
    scarf.name = "Bufanda"
    scarf.scale = (1.1, 0.9, 0.72)
    finish(scarf, cloth, bevel=0.002, smooth=True)
    curve_trim("Capa_Ornamento", [
        (0, 0.216, 1.46), (-0.12, 0.216, 1.29), (0, 0.218, 1.10),
        (0.13, 0.216, 0.91), (0, 0.218, 0.69), (-0.13, 0.216, 0.91),
        (0, 0.218, 1.10), (0.12, 0.216, 1.29), (0, 0.216, 1.46)
    ], 0.012, leather)

    # Identificación del recurso y función de cada pieza.
    for obj in BODY_OBJECTS:
        obj["tenfe_asset"] = "PaladinSoldier_v2"
        obj["reference_source"] = "Imágenes ortográficas proporcionadas por el usuario"
        obj["rig_ready_pose"] = "relaxed_A_pose"

    return {"steel": steel, "bright": bright, "bronze": bronze, "leather": leather}


def build_sword(materials):
    steel = materials["bright"]
    dark = materials["steel"]
    bronze = materials["bronze"]
    leather = materials["leather"]
    # El origen queda en el centro de la empuñadura para facilitar la rotación.
    cube("Espada_Empuñadura", (0, 0, 0), (0.055, 0.055, 0.24), leather,
         bevel=0.008, group="sword")
    sphere("Espada_Pomo", (0, 0, -0.15), (0.065, 0.065, 0.065), bronze, group="sword")
    curve_trim("Espada_Guarda", [(-0.25, 0, 0.14), (-0.12, 0, 0.18),
                                  (0, 0, 0.15), (0.12, 0, 0.18), (0.25, 0, 0.14)],
               0.028, bronze, group="sword")
    cube("Espada_Hoja", (0, 0, 0.72), (0.085, 0.018, 1.10), steel,
         bevel=0.006, group="sword")
    cube("Espada_Canal", (0, -0.012, 0.73), (0.018, 0.008, 0.91), dark,
         bevel=0.003, group="sword")
    cone("Espada_Punta", (0, 0, 1.33), 0.047, 0.0, 0.14, steel,
         vertices=4, bevel=0.003, group="sword")
    for obj in SWORD_OBJECTS:
        obj["tenfe_asset"] = "PaladinGreatsword"


def add_preview_environment():
    floor_mat = make_material("M_Suelo_Preview", (0.035, 0.04, 0.05), 0.0, 0.82)
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, -0.005))
    floor = bpy.context.object
    floor.name = "Preview_Floor"
    floor.data.materials.append(floor_mat)

    scene = bpy.context.scene
    world = scene.world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.018, 0.022, 0.030, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.28

    def area(name, location, energy, color, size):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.color = color
        data.shape = "DISK"
        data.size = size
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        obj.location = location
        point_at(obj, Vector((0, 0, 1.02)))

    area("Luz_Principal", (-2.7, -3.2, 3.5), 760, (1.0, 0.72, 0.48), 2.1)
    area("Luz_Contorno", (2.4, 1.8, 2.9), 900, (0.32, 0.46, 1.0), 1.7)
    area("Luz_Relleno", (0.4, -3.2, 1.2), 410, (0.80, 0.87, 1.0), 1.4)

    camera_data = bpy.data.cameras.new("Camera_Preview")
    camera = bpy.data.objects.new("Camera_Preview", camera_data)
    bpy.context.collection.objects.link(camera)
    camera_data.lens = 66
    camera.location = (2.8, -4.5, 2.35)
    point_at(camera, Vector((0, 0, 1.03)))
    scene.camera = camera
    return camera


def point_at(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def export_selected(objects, filepath):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.fbx(
        filepath=str(filepath), use_selection=True, object_types={"MESH"},
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", global_scale=1.0,
        axis_forward="-Y", axis_up="Z", use_mesh_modifiers=True,
        mesh_smooth_type="FACE", add_leaf_bones=False, bake_anim=False, path_mode="AUTO"
    )


def save_render_export(camera):
    for path in (BLEND_FILE, BODY_FBX, SWORD_FBX, PREVIEW_FRONT, PREVIEW_BACK):
        path.parent.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 760
    scene.render.resolution_y = 980
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.15

    # La espada se exporta como pieza independiente y no aparece en las vistas de armadura.
    for obj in SWORD_OBJECTS:
        obj.hide_render = True

    scene.render.filepath = str(PREVIEW_FRONT)
    bpy.ops.render.render(write_still=True)
    camera.location = (-2.7, 4.3, 2.25)
    point_at(camera, Vector((0, 0.02, 1.03)))
    scene.render.filepath = str(PREVIEW_BACK)
    bpy.ops.render.render(write_still=True)

    try:
        bpy.ops.file.pack_all()
    except RuntimeError:
        pass
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_FILE))
    export_selected(BODY_OBJECTS, BODY_FBX)
    export_selected(SWORD_OBJECTS, SWORD_FBX)


def main():
    reset_scene()
    add_reference_images()
    materials = build_body()
    build_sword(materials)
    camera = add_preview_environment()
    save_render_export(camera)
    print(f"TENFE_PALADIN_V2_BODY_PARTS={len(BODY_OBJECTS)}")
    print(f"TENFE_PALADIN_V2_SWORD_PARTS={len(SWORD_OBJECTS)}")
    print(f"TENFE_PALADIN_V2_BLEND={BLEND_FILE}")
    print(f"TENFE_PALADIN_V2_BODY_FBX={BODY_FBX}")
    print(f"TENFE_PALADIN_V2_SWORD_FBX={SWORD_FBX}")
    print(f"TENFE_PALADIN_V2_PREVIEW={PREVIEW_FRONT}")


if __name__ == "__main__":
    main()
