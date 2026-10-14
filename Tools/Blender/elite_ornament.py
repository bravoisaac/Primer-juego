"""Locally authored PBR materials and fitted relief for the siege paladin.

This module uses only Blender's bundled Python, mathutils and NumPy. Materials
use regular image/Principled nodes, so their color, roughness and tangent normal
textures survive glTF export. Meshes need UVs; all images are packed in the blend.
The ornament is actual geometry, independent from texture resolution.
"""

from __future__ import annotations

import math
from collections.abc import Callable

import bpy
import numpy as np
from mathutils import Vector


def _image(name: str, pixels: np.ndarray, *, data: bool = False):
    existing = bpy.data.images.get(name)
    if existing is not None:
        return existing
    height, width = pixels.shape[:2]
    image = bpy.data.images.new(name, width=width, height=height, alpha=False)
    image.colorspace_settings.name = "Non-Color" if data else "sRGB"
    rgba = np.ones((height, width, 4), dtype=np.float32)
    if pixels.ndim == 2:
        rgba[:, :, :3] = pixels[:, :, None]
    else:
        rgba[:, :, :3] = pixels[:, :, :3]
    image.pixels.foreach_set(np.clip(rgba, 0.0, 1.0).ravel())
    image.update()
    image.pack()
    return image


def _smooth(field: np.ndarray, iterations: int = 1):
    for _ in range(iterations):
        field = (field * 4.0 + np.roll(field, 1, 0) + np.roll(field, -1, 0)
                 + np.roll(field, 1, 1) + np.roll(field, -1, 1)) / 8.0
    return field


def _normal(height: np.ndarray, strength: float):
    # Central differences wrap at tile boundaries; the normal map tiles too.
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * strength
    dy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * strength
    normal = np.stack((-dx, -dy, np.ones_like(dx)), axis=-1)
    normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
    return normal * 0.5 + 0.5


def _etched_acanthus(size):
    """Original chased foliage, rasterized for sub-millimetre steel engraving."""
    n=256
    tile=np.zeros((n,n),dtype=np.float32)
    paths=[]
    stem=_bezier((.5,.02),(.40,.33),(.58,.70),(.5,.98),180)
    paths.append(stem)
    for side in (-1,1):
        for index in range(5):
            y=.12+index*.145
            leaf,vein=_leaf((.5,y),(.5+side*(.30-.025*index),y+.24),bend=side*.025,width=.050)
            paths.extend((leaf,vein))
        paths.append(_bezier((.5,.10),(.5+side*.54,.13),(.5+side*.54,.55),(.5+side*.29,.64),150))
        paths.append(_bezier((.5+side*.29,.64),(.5+side*.10,.67),(.5+side*.14,.45),(.5+side*.26,.49),110))
    for path in paths:
        for p0,p1 in zip(path[:-1],path[1:]):
            steps=max(2,int(math.dist(p0,p1)*n*2))
            t=np.linspace(0,1,steps)
            px=np.rint((p0[0]+(p1[0]-p0[0])*t)*(n-1)).astype(int)%n
            py=np.rint((p0[1]+(p1[1]-p0[1])*t)*(n-1)).astype(int)%n
            np.maximum.at(tile,(py,px),1)
    tile=_smooth(tile,1)
    yy,xx=np.mgrid[:size,:size]
    row=np.floor(yy/size*6).astype(int)
    tx=(((xx/size*5+(row%2)*.5)%1)*n).astype(int)
    ty=(((yy/size*6)%1)*n).astype(int)
    return tile[ty,tx]


def _metal_maps(size: int, seed: int):
    rng = np.random.default_rng(seed)
    grain = _smooth(rng.normal(0.0, 1.0, (size, size)).astype(np.float32), 2)
    grain /= max(float(grain.std()), 0.0001)
    scratches = np.zeros((size, size), dtype=np.float32)
    # Fine broken tool marks, primarily oblique, never large cloudy noise.
    for _ in range(1450):
        x = rng.uniform(0, size)
        y = rng.uniform(0, size)
        length = rng.uniform(5, 58)
        angle = rng.normal(-0.50, 0.28) if rng.random() < 0.77 else rng.uniform(0, math.tau)
        steps = max(5, int(length * 1.8))
        t = np.linspace(0, 1, steps)
        xx = ((x + np.cos(angle) * length * t).astype(np.int32)) % size
        yy = ((y + np.sin(angle) * length * t).astype(np.int32)) % size
        value = np.sin(t * math.pi) * rng.uniform(0.15, 0.65)
        np.maximum.at(scratches, (yy, xx), value)
    pits = (rng.random((size, size)) > 0.997).astype(np.float32)
    fine = _smooth(rng.random((size, size)).astype(np.float32), 1) - 0.5
    machining = np.sin(np.arange(size, dtype=np.float32)[None, :] * 1.93)
    height = grain * 0.006 + fine * 0.020 - scratches * 0.10 - pits * 0.045
    height += machining * 0.003
    engraving=_etched_acanthus(size)
    height-=engraving*.11
    # Smooth random fractal fields, not directional sine bands on the armour.
    patina = np.zeros((size,size),dtype=np.float32)
    yy,xx=np.mgrid[:size,:size].astype(np.float32)
    for grid,weight in ((6,.56),(17,.29),(53,.15)):
        lattice=rng.random((grid,grid),dtype=np.float32)*2-1
        gx=xx/size*grid;gy=yy/size*grid
        ix=np.floor(gx).astype(int);iy=np.floor(gy).astype(int)
        fx=gx-ix;fy=gy-iy;fx=fx*fx*(3-2*fx);fy=fy*fy*(3-2*fy)
        layer=(lattice[iy%grid,ix%grid]*(1-fx)*(1-fy)
               +lattice[iy%grid,(ix+1)%grid]*fx*(1-fy)
               +lattice[(iy+1)%grid,ix%grid]*(1-fx)*fy
               +lattice[(iy+1)%grid,(ix+1)%grid]*fx*fy)
        patina+=weight*layer
    roughness = np.clip(0.46 + grain * 0.031 + scratches * 0.17 + pits * 0.12
                        + patina * .035 + engraving*.16, 0.31, 0.72)
    color_mod = (1.0 + grain[:, :, None] * 0.026 - scratches[:, :, None] * 0.15
                 + patina[:, :, None] * .055 - engraving[:,:,None]*.28)
    return color_mod, roughness, _normal(height, 2.5)


def _material(name, base, roughness, normal, metallic, roughness_value):
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (630, 80)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (310, 80)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness_value
    bsdf.inputs["IOR"].default_value = 1.45
    mat.node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    for label, im, position, socket in (
        ("Base Color", base, (-600, 320), "Base Color"),
        ("Roughness", roughness, (-600, 40), "Roughness"),
    ):
        tex = nodes.new("ShaderNodeTexImage")
        tex.name = label
        tex.label = label + " · locally authored"
        tex.image = im
        tex.location = position
        tex.interpolation = "Linear"
        tex.extension = "REPEAT"
        mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs[socket])
    tex = nodes.new("ShaderNodeTexImage")
    tex.name = "Tangent Normal"
    tex.image = normal
    tex.location = (-600, -230)
    tex.interpolation = "Linear"
    normal_node = nodes.new("ShaderNodeNormalMap")
    normal_node.location = (-150, -180)
    normal_node.inputs["Strength"].default_value = 0.38
    mat.node_tree.links.new(tex.outputs["Color"], normal_node.inputs["Color"])
    mat.node_tree.links.new(normal_node.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*tuple(base.pixels[:3]), 1.0)
    mat["origin"] = "Original procedural surface by Codex; no external texture assets"
    return mat


def create_materials() -> dict:
    """Return steel, dark_steel, gold, black and leather Blender materials.

    Steel and brass textures are 1024². Leather/black detail is 512². Image maps
    are packed; no files or services are downloaded. This function is idempotent.
    """
    if all(bpy.data.materials.get("Elite." + key) for key in
           ("steel", "dark_steel", "gold", "black", "leather")):
        return {key: bpy.data.materials["Elite." + key] for key in
                ("steel", "dark_steel", "gold", "black", "leather")}

    modulation, rough, norm = _metal_maps(1024, 14102026)
    metal_rough = _image("ElitePBR.Steel.Roughness", rough, data=True)
    metal_norm = _image("ElitePBR.Steel.Normal", norm, data=True)
    steel_color = _image("ElitePBR.Steel.Color", modulation * np.array((0.335, 0.337, 0.329)))
    dark_color = _image("ElitePBR.DarkSteel.Color", modulation * np.array((0.155, 0.178, 0.194)))
    brass_color = _image("ElitePBR.Brass.Color", modulation * np.array((0.380, 0.292, 0.181)))
    brass_rough = _image("ElitePBR.Brass.Roughness", np.clip(rough + 0.13, 0, 1), data=True)

    rng = np.random.default_rng(921)
    leather_grain = _smooth(rng.random((512, 512)).astype(np.float32), 2) - 0.5
    yy, xx = np.mgrid[:512, :512]
    pore = np.cos(xx * 0.93 + np.sin(yy * 0.12)) * np.sin(yy * 1.03 + xx * 0.07)
    leather_height = leather_grain * 0.08 + pore * 0.008
    leather_normal = _image("ElitePBR.Leather.Normal", _normal(leather_height, 2.0), data=True)
    leather_rough = _image("ElitePBR.Leather.Roughness", 0.72 + leather_grain * 0.20, data=True)
    leather_color = _image("ElitePBR.Leather.Color", (1 + leather_grain[:, :, None] * 0.3)
                           * np.array((0.115, 0.071, 0.048)))
    black_color = _image("ElitePBR.Black.Color", (1 + leather_grain[:, :, None] * 0.2)
                         * np.array((0.027, 0.031, 0.033)))
    return {
        "steel": _material("Elite.steel", steel_color, metal_rough, metal_norm, 0.88, 0.38),
        "dark_steel": _material("Elite.dark_steel", dark_color, metal_rough, metal_norm, 0.86, 0.42),
        "gold": _material("Elite.gold", brass_color, brass_rough, metal_norm, 0.83, 0.51),
        "black": _material("Elite.black", black_color, leather_rough, leather_normal, 0.1, 0.70),
        "leather": _material("Elite.leather", leather_color, leather_rough, leather_normal, 0.0, 0.73),
    }


def _bezier(a, b, c, d, samples=24):
    a, b, c, d = [np.array(point, dtype=float) for point in (a, b, c, d)]
    return [tuple((1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t*t*c + t**3*d)
            for t in np.linspace(0, 1, samples)]


def _leaf(base, tip, bend=0.0, width=0.017):
    """Two sinuous arcs meeting in a narrow pointed acanthus leaf."""
    base, tip = np.array(base), np.array(tip)
    delta = tip - base
    perpendicular = np.array((-delta[1], delta[0]))
    perpendicular /= max(np.linalg.norm(perpendicular), 1e-8)
    a = _bezier(base, base + delta * 0.27 + perpendicular * (width + bend),
                base + delta * 0.78 + perpendicular * (width + bend), tip, 20)
    b = _bezier(tip, base + delta * 0.69 + perpendicular * (-width * 0.4 + bend),
                base + delta * 0.15 - perpendicular * width * 0.5, base, 20)
    vein = _bezier(base, base + delta * .30 + perpendicular * bend * .6,
                   base + delta * .72 + perpendicular * bend * .5, tip, 15)
    return a + b[1:], vein


def _reflect(path):
    return [(1.0-u, v) for u, v in path]


def _curve_object(name, paths, surface, collection, material, radius):
    if not paths:
        return None
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 1
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    curve.use_fill_caps = True
    for path in paths:
        spline = curve.splines.new("POLY")
        spline.points.add(len(path) - 1)
        flat = []
        for u, v in path:
            # Fail early if an ornament edit spills outside the panel interior.
            if not (0.099 <= u <= 0.901 and 0.099 <= v <= 0.901):
                raise ValueError(f"Ornament point outside panel: {(u, v)}")
            p = surface(float(u), float(v))
            flat.extend((p[0], p[1], p[2], 1.0))
        spline.points.foreach_set("co", flat)
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    curve.materials.append(material)
    obj["detail"] = "Surface-fitted hand-designed acanthus and lance relief"
    return obj


def decorate_panel(name: str, surface: Callable, collection, gold, dark=None,
                   density: float = 1.0) -> list:
    """Fit original symmetric filigree to an existing curved armor panel.

    ``surface(u, v)`` returns a 3D point, including the caller's desired relief
    offset. u and v span 0..1; this function stays inside 0.10..0.90. v should
    increase up the ornament. The callback may use world or local coordinates;
    returned objects have identity transforms and inherit none of the panel's.
    ``collection`` receives 2 (or 3 with dark) batched Curve objects. Convert
    these curves to meshes when exporting GLB. All strokes are 0.55–0.85 mm.
    ``density`` adjusts leaf repeats, from 0.35 (simple) to 1.6 (elaborate).
    """
    density = max(0.35, min(float(density), 1.6))
    primary, fine, cut = [], [], []

    # A restrained central spearhead, elongated like a votive cathedral finial.
    spear = _bezier((.50,.88), (.477,.810), (.429,.721), (.454,.639), 24)
    spear += _bezier((.454,.639), (.468,.650), (.482,.666), (.50,.682), 14)[1:]
    primary.extend([spear, _reflect(spear)])
    primary.append(_bezier((.50,.156), (.486,.410), (.519,.598), (.50,.855), 44))
    fine.append(_bezier((.50,.20), (.510,.394), (.505,.576), (.50,.803), 36))

    # Thorn-like sweeping foot, visually anchors the long stem to a point.
    foot = _bezier((.50,.145), (.476,.190), (.420,.209), (.408,.263), 22)
    primary.extend([foot, _reflect(foot)])
    foot_leaf, foot_vein = _leaf((.459,.214), (.383,.286), bend=.01, width=.020)
    for path in (foot_leaf, _reflect(foot_leaf)):
        primary.append(path)
    fine.extend([foot_vein, _reflect(foot_vein)])

    # Organic ascending tendril. The mirrored pair leaves clean negative space.
    stem_a = _bezier((.494,.258), (.319,.341), (.189,.378), (.222,.562), 36)
    stem_b = _bezier((.222,.562), (.245,.704), (.404,.811), (.403,.679), 32)
    stem_c = _bezier((.403,.679), (.402,.632), (.327,.627), (.333,.684), 22)
    stem = stem_a + stem_b[1:] + stem_c[1:]
    primary.extend([stem, _reflect(stem)])

    # Each branch is an authored, non-circular leaf. Fine veins are separate
    # splines batched together so the scene remains easy to manipulate.
    leaves = [
        ((.353,.341),(.204,.372), .010,.025),
        ((.289,.391),(.155,.443), .012,.026),
        ((.239,.459),(.139,.552), .015,.024),
        ((.224,.531),(.156,.642), .010,.022),
        ((.240,.614),(.217,.735), -.003,.021),
        ((.287,.691),(.297,.799), -.008,.022),
        ((.349,.724),(.375,.828), -.007,.017),
        ((.287,.404),(.354,.477), -.008,.020),
        ((.228,.489),(.318,.557), -.012,.022),
        ((.237,.579),(.315,.627), -.008,.018),
    ]
    keep = max(4, min(len(leaves), round(7 * density)))
    # Even distribution preserves upper and lower visual balance at low density.
    chosen = sorted(set(round(i*(len(leaves)-1)/max(keep-1,1)) for i in range(keep)))
    for index in chosen:
        base, tip, bend, width = leaves[index]
        outline, vein = _leaf(base, tip, bend=bend, width=width)
        primary.extend([outline, _reflect(outline)])
        fine.extend([vein, _reflect(vein)])
        if density >= 1.0:
            midpoint = ((base[0]+tip[0])*.5, (base[1]+tip[1])*.5)
            flanking = _bezier(base, (base[0]+.005,base[1]+.012),
                               (midpoint[0]+.009,midpoint[1]+.006), midpoint, 10)
            fine.extend([flanking, _reflect(flanking)])

    # A smaller crown-leaf echo above the scrolling vine.
    top_leaf, top_vein = _leaf((.473,.771), (.422,.859), bend=-.009, width=.014)
    primary.extend([top_leaf, _reflect(top_leaf)])
    fine.extend([top_vein, _reflect(top_vein)])
    if density > 1.15:
        bud = _bezier((.421,.486),(.399,.568),(.440,.597),(.463,.548),20)
        primary.extend([bud,_reflect(bud)])
        petal, vein = _leaf((.421,.486),(.370,.559),bend=.01,width=.014)
        primary.extend([petal,_reflect(petal)])
        fine.extend([vein,_reflect(vein)])

    objects = []
    if dark is not None:
        # Sparse fine engraved echoes, kept separate from the raised brass.
        left_cut = _bezier((.363,.236), (.206,.275), (.123,.337), (.136,.404), 30)
        cut.extend([left_cut, _reflect(left_cut)])
        upper_cut = _bezier((.138,.687),(.172,.792),(.284,.868),(.347,.873),26)
        cut.extend([upper_cut,_reflect(upper_cut)])
        obj = _curve_object(name + ".EngravedEcho", cut, surface, collection, dark, .00055)
        if obj:
            objects.append(obj)
    for suffix, paths, radius in ((".AcanthusRelief",primary,.00070),
                                   (".VeinRelief",fine,.00055)):
        obj = _curve_object(name + suffix, paths, surface, collection, gold, radius)
        if obj:
            objects.append(obj)
    return objects
