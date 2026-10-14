"""Original cloth for the Ten Fe siege elite, built entirely inside Blender.

Call ``build_textiles(collection)`` after creating the armour. Coordinates are
metres, Z up, facing -Y; nominal total character height is 2.16 m. The cloth
mesh, damask artwork, tangent normal map, seams and torn threads are authored
mathematically here. There are no downloaded textures or external generators.
Materials use packed image textures supported by Blender's glTF exporter.
"""

import math
import random

import bpy
import numpy as np
from mathutils import Vector


TAU = math.tau


def _principled(material):
    """Locate by node type; saved UI language can translate default names."""
    nodes = material.node_tree.nodes
    shader = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
    if shader is None:
        shader = nodes.new('ShaderNodeBsdfPrincipled')
    output = next((node for node in nodes if node.type == 'OUTPUT_MATERIAL'), None)
    if output is None:
        output = nodes.new('ShaderNodeOutputMaterial')
    if not output.inputs['Surface'].is_linked:
        material.node_tree.links.new(shader.outputs['BSDF'], output.inputs['Surface'])
    return shader


def _image(name, pixels, non_color=False):
    height, width = pixels.shape[:2]
    image = bpy.data.images.new(name, width=width, height=height, alpha=True)
    image.colorspace_settings.name = 'Non-Color' if non_color else 'sRGB'
    image.pixels.foreach_set(np.ascontiguousarray(pixels, dtype=np.float32).ravel())
    image.update()
    image.pack()
    return image


def _damask_images():
    """Draw a tiny acanthus tapestry tile, then weave it into a 1K textile.

    Cubic leaves and scrolling branches replace circular ornament primitives.
    Different masks describe the figured yarn, its raised edge, and old wear.
    """
    size = 256
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    x, y = (xx + .5) / size, (yy + .5) / size
    motif = np.zeros((size, size), dtype=np.float32)
    veins = np.zeros_like(motif)

    def polygon(points, target, value=1.):
        inside = np.zeros_like(motif, dtype=bool)
        px, py = points[-1]
        for qx, qy in points:
            crossing = ((py > y) != (qy > y)) & (
                x < (qx - px) * (y - py) / (qy - py + 1e-12) + px)
            inside ^= crossing
            px, py = qx, qy
        target[inside] = np.maximum(target[inside], value)

    def cubic(points, count=30):
        p = np.array(points, dtype=float)
        return [tuple((1-t)**3*p[0] + 3*(1-t)**2*t*p[1]
                      + 3*(1-t)*t*t*p[2] + t**3*p[3])
                for t in np.linspace(0, 1, count)]

    def stroke(points, radius, target, value=1.):
        for (ax, ay), (bx, by) in zip(points[:-1], points[1:]):
            dx, dy = bx-ax, by-ay
            t = np.clip(((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy+1e-12), 0, 1)
            distance = np.sqrt((x-ax-t*dx)**2+(y-ay-t*dy)**2)
            alpha = np.clip((radius-distance)*size + .5, 0, 1)*value
            np.maximum(target, alpha, out=target)

    stem = cubic([(.5, .02), (.435, .32), (.53, .7), (.5, .95)])
    stroke(stem, .010, motif, .8)
    stroke(stem, .003, veins)
    # Pairs of tapering acanthus leaves, swept upward into an elongated crown.
    for side in [-1, 1]:
        for index, (root_y, tip_x, tip_y) in enumerate([
                (.16, .16, .35), (.29, .085, .53), (.43, .14, .72),
                (.57, .24, .84), (.7, .35, .91)]):
            tip = (.5 + side*(.5-tip_x), tip_y)
            root = (.5 + side*.012, root_y)
            spread = .12 if index < 3 else .065
            edge1 = cubic([root, (.5+side*spread, root_y-.005),
                           (tip[0]-side*.018, tip_y-.13), tip])
            edge2 = cubic([tip, (tip[0]+side*.095, tip_y-.16),
                           (.5+side*.14, root_y-.07), root])
            polygon(edge1+edge2, motif, .85)
            mid = cubic([root, (.5+side*.10, root_y+.025),
                         (tip[0]+side*.01, tip_y-.12), tip])
            stroke(mid, .0028, veins, .82)
        # The open scroll around the palmette connects adjoining tiles.
        scroll = cubic([(.5+side*.025, .045), (.5+side*.54, .12),
                        (.5+side*.46, .51), (.5+side*.35, .55)])
        stroke(scroll, .0065, motif, .72)
        curl = cubic([scroll[-1], (.5+side*.24, .61),
                      (.5+side*.23, .43), (.5+side*.31, .45)])
        stroke(curl, .005, motif, .7)
        tiny = cubic([(.5+side*.38, .24), (.5+side*.56, .34),
                      (.5+side*.49, .63), (.5+side*.50, .75)])
        stroke(tiny, .0045, motif, .58)
    crown_left = cubic([(.5, .99), (.375, .88), (.445, .8), (.5, .75)])
    crown_right = [(1-a,b) for a,b in reversed(crown_left)]
    polygon(crown_left+crown_right, motif, .95)
    stroke([(.5, .78), (.5, .975)], .003, veins, .85)
    # Shallow diamond framework, broken enough to read as brocade.
    for points in [[(0,.5),(.21,.84),(.5,1.)],
                   [(.5,0.),(.79,.16),(1.,.5)]]:
        stroke(points, .0035, motif, .36)

    out_size = 1024
    yy, xx = np.mgrid[0:out_size, 0:out_size].astype(np.float32)
    u, v = xx / out_size, yy / out_size
    tile_v = np.floor(v*7).astype(int)
    tx = ((u*4 + (tile_v % 2)*.5) % 1 * size).astype(int)
    ty = ((v*7) % 1 * size).astype(int)
    figured = motif[ty, tx]
    vein = veins[ty, tx]
    rng = np.random.default_rng(14619)
    noise = rng.random((out_size, out_size), dtype=np.float32)-.5
    coarse = (np.sin(u*37+np.sin(v*19))*np.cos(v*23-u*11)
              + .5*np.sin(u*93+v*47))*.5
    weave = np.sin(xx*math.pi*.5)*np.cos(yy*math.pi*.5)
    wear = .73+.15*np.sin(u*18+v*11)+.08*np.cos(v*59-u*27)
    delta = figured*.083*wear - vein*.042 + noise*.022 + weave*.007 + coarse*.013
    color = np.empty((out_size, out_size, 4), dtype=np.float32)
    color[:,:,0] = .255 + delta
    color[:,:,1] = .169 + delta*.83
    color[:,:,2] = .109 + delta*.63
    color[:,:,3] = 1.
    # Uneven edge erosion is baked into the image; geometry carries real tears.
    grime = np.clip((.11-v)/.11, 0, 1)*(.025+.012*np.sin(u*85))
    color[:,:,:3] -= grime[:,:,None]
    color[:,:,:3] = np.clip(color[:,:,:3], .015, .7)
    # Blender's float pixel API stores linear light; keep cocoa wool dark.
    color[:,:,:3] *= .24

    height = figured*.6-vein*.32+noise*.17+weave*.12
    dy, dx = np.gradient(height)
    normal = np.stack((-dx*.85, -dy*.85, np.ones_like(dx)), axis=-1)
    normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
    normal_rgba = np.ones_like(color)
    normal_rgba[:,:,:3] = normal*.5+.5
    return (_image('Elite_Tapestry_BaseColor_1K', color),
            _image('Elite_Tapestry_TangentNormal_1K', normal_rgba, True))


def _materials():
    base_image, normal_image = _damask_images()
    material = bpy.data.materials.new('Elite | umber acanthus wool tapestry')
    material.diffuse_color = (.13, .073, .04, 1.)
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    shader = _principled(material)
    shader.inputs['Roughness'].default_value = .91
    if 'Sheen Weight' in shader.inputs:
        shader.inputs['Sheen Weight'].default_value = .22
    base = nodes.new('ShaderNodeTexImage')
    base.name = 'Original acanthus damask artwork'
    base.image = base_image
    links.new(base.outputs['Color'], shader.inputs['Base Color'])
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = normal_image
    normal = nodes.new('ShaderNodeNormalMap')
    normal.inputs['Strength'].default_value = .32
    links.new(tex.outputs['Color'], normal.inputs['Color'])
    links.new(normal.outputs['Normal'], shader.inputs['Normal'])

    plain = bpy.data.materials.new('Elite | scarf matte walnut wool')
    plain.diffuse_color = (.025, .012, .006, 1)
    plain.use_nodes = True
    p = _principled(plain)
    p.inputs['Base Color'].default_value = plain.diffuse_color
    p.inputs['Roughness'].default_value = .94
    if 'Sheen Weight' in p.inputs:
        p.inputs['Sheen Weight'].default_value = .08
    # Dedicated packed wool albedo avoids a uniform plastic-looking scarf.
    # Image values are sRGB: approximately .025/.012/.006 in linear light.
    yy,xx = np.mgrid[0:1024,0:1024].astype(np.float32)
    rng = np.random.default_rng(24417)
    noise = rng.random((1024,1024),dtype=np.float32)-.5
    warp = np.cos(xx*TAU/3.7)*np.cos(yy*TAU/3.7)
    fleck = np.sin(xx*.147+np.sin(yy*.15))*np.sin(yy*.08)
    wool = np.ones((1024,1024,4),dtype=np.float32)
    variation = noise*.031+warp*.014+fleck*.008
    wool[:,:,0] = .172+variation
    wool[:,:,1] = .112+variation*.78
    wool[:,:,2] = .071+variation*.55
    wool[:,:,:3] *= .20
    wool_color = _image('Elite_Scarf_CocoaWool_BaseColor_1K',wool)
    yarn_height = warp*.36+noise*.28+np.sin(xx*1.65+yy*.34)*.09
    dy,dx = np.gradient(yarn_height)
    normals = np.stack((-dx,-dy,np.ones_like(dx)),axis=-1)
    normals /= np.linalg.norm(normals,axis=-1,keepdims=True)
    wool[:,:,:3] = normals*.5+.5
    wool_normal = _image('Elite_Scarf_WovenNormal_1K',wool,True)
    color_tex = plain.node_tree.nodes.new('ShaderNodeTexImage')
    color_tex.image = wool_color
    plain.node_tree.links.new(color_tex.outputs['Color'],p.inputs['Base Color'])
    tex = plain.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image = wool_normal
    normal = plain.node_tree.nodes.new('ShaderNodeNormalMap')
    normal.inputs['Strength'].default_value = .62
    plain.node_tree.links.new(tex.outputs['Color'], normal.inputs['Color'])
    plain.node_tree.links.new(normal.outputs['Normal'], p.inputs['Normal'])

    seam = bpy.data.materials.new('Elite | age-darkened braid and frayed threads')
    seam.diffuse_color = (.026, .014, .008, 1)
    seam.use_nodes = True
    _principled(seam).inputs['Base Color'].default_value = seam.diffuse_color
    _principled(seam).inputs['Roughness'].default_value = .93
    embroidery = bpy.data.materials.new('Elite | faded ochre embroidered yarn')
    embroidery.diffuse_color = (.060, .037, .018, 1.)
    embroidery.use_nodes = True
    p = _principled(embroidery)
    p.inputs['Base Color'].default_value = embroidery.diffuse_color
    p.inputs['Roughness'].default_value = .81
    p.inputs['Metallic'].default_value = .1
    return material, plain, seam, embroidery


def _mesh(name, vertices, faces, uv, material, collection, thickness=.002):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(material)
    layer = mesh.uv_layers.new(name='ClothUV')
    for poly in mesh.polygons:
        poly.use_smooth = True
        for loop_index in poly.loop_indices:
            layer.data[loop_index].uv = uv[mesh.loops[loop_index].vertex_index]
    if thickness:
        modifier = obj.modifiers.new('Real woven thickness', 'SOLIDIFY')
        modifier.thickness = thickness
        modifier.offset = 0.
        # Uneven torn boundaries can make even-offset mitres explode into
        # long spikes. A constant normal offset preserves the thin cloth.
        modifier.use_even_offset = False
    obj['authorship'] = 'Original local procedural textile; no external generation'
    return obj


def _curves(name, paths, material, collection, radius=.0008):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = 1
    data.bevel_depth = radius
    data.bevel_resolution = 1
    for path in paths:
        spline = data.splines.new('POLY')
        spline.points.add(len(path)-1)
        for point, co in zip(spline.points, path):
            point.co = (*co, 1)
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    data.materials.append(material)
    return obj


def _cape_point(u, v):
    """Surface parameter u left/right, v from shoulders to frayed lower hem."""
    width = .247+.186*(v**.63)
    hem = (.296 + .043*math.sin(u*TAU*3.2+.2)
           + .019*math.sin(u*TAU*13.7) + .024*math.sin(u*TAU*8.3+1.8))
    # Tall, narrow V cuts in the silhouette, independent of interior holes.
    for location, depth, spread in [(.06,.10,.022),(.23,.15,.027),
                                   (.42,.085,.019),(.67,.13,.024),(.89,.12,.027)]:
        hem += depth*max(0, 1-abs(u-location)/spread)
    x = (u*2-1)*width+.013*math.sin(v*math.pi*1.5)
    x += (v**5)*.0035*math.sin(v*97+u*TAU*19)
    z = 1.729*(1-v)+hem*v
    z += .012*math.sin(u*TAU*2.3)*math.sin(v*math.pi)
    fold_phase = u*TAU*5.5 + .4*math.sin(v*5) + .12*math.sin(u*TAU*2)
    fold = (.009+.023*math.sin(v*math.pi*.8))*math.cos(fold_phase)
    fold += .005*math.sin(u*TAU*12.5-v*6)*(v*.7+.3)
    y = .18+.10*(1-math.exp(-v*10))+.078*v + fold
    y -= .07*abs(2*u-1)**4*(1-v)**4
    y += .018*math.sin(v*math.pi*2+u*5)*v
    return (x,y,z)


def _cape_hole(u, v):
    for cx, cy, rx, ry in [(.135,.955,.011,.035),(.326,.915,.008,.030),
                            (.518,.977,.014,.042),(.76,.927,.009,.037),
                            (.92,.984,.014,.03),(.62,.955,.006,.017),
                            (.82,.87,.005,.014),(.206,.97,.005,.014)]:
        du = (u-cx)/rx
        dv = (v-cy)/ry
        wobble = .20*math.sin(u*1380+v*460)+.12*math.sin(v*920)
        if du*du+dv*dv < 1+wobble:
            return True
    return False


def _cape(material, seam, embroidery, collection):
    nu, nv = 156, 248
    vertices, uv, faces = [], [], []
    for j in range(nv+1):
        v = j/nv
        for i in range(nu+1):
            u = i/nu
            vertices.append(_cape_point(u,v))
            uv.append((u,1-v))
    for j in range(nv):
        for i in range(nu):
            if _cape_hole((i+.5)/nu, (j+.5)/nv):
                continue
            a = j*(nu+1)+i
            # Outside faces toward +Y.
            faces.append((a,a+1,a+nu+2,a+nu+1))
    objects = [_mesh('Elite_Cape | tailored brocade with torn hem', vertices,
                     faces, uv, material, collection)]
    paths = []
    for u in [.007,.993]:
        paths.append([_cape_point(u,j/130) for j in range(131)])
    paths.append([_cape_point(i/200,.996) for i in range(201)])
    objects.append(_curves('Elite_Cape | dark bound edges', paths, seam,
                           collection, .00125))
    # Interrupted sewn border has two rails and sinuous hand-sewn filling.
    paths = []
    for edge in [0.,1.]:
        sign = 1 if edge == 0 else -1
        for inset in [.022,.041]:
            paths.append([tuple(Vector(_cape_point(edge+sign*inset,j/180))
                                +Vector((0,.0024,0))) for j in range(162)])
        paths.append([tuple(Vector(_cape_point(edge+sign*(.0315+.007*math.sin(j*.54)),j/240))
                            +Vector((0,.0026,0))) for j in range(215)])
    objects.append(_curves('Elite_Cape | worn ochre running-stitch border',
                           paths, embroidery, collection, .00063))
    rng = random.Random(778)
    paths = []
    for i in range(205):
        u = (i+rng.random())/206
        start = Vector(_cape_point(u, .997))
        length = rng.uniform(.004,.027)
        paths.append([tuple(start), tuple(start+Vector((rng.uniform(-.004,.004),.001,-length*.5))),
                      tuple(start+Vector((rng.uniform(-.006,.006),rng.uniform(-.003,.004),-length)))])
    # A few loose warp threads still span holes near the bottom of the cloth.
    for u,v in [(.13,.95),(.325,.91),(.513,.974),(.76,.925),(.92,.98)]:
        for offset in [-.002, .002]:
            paths.append([_cape_point(u+offset,v+d) for d in [-.026,-.006,.018,.028]])
    objects.append(_curves('Elite_Cape | broken warp fibres',paths,seam,
                           collection,.00048))
    return objects


def _cowl_point(theta, w):
    front = max(0., math.cos(theta))
    phase = w*math.pi*6.7+.79*math.sin(theta*2)+.2*math.sin(theta*5)
    wave = math.sin(phase)
    fold = (.0038+.0042*front)*math.copysign(abs(wave)**.58,wave)
    fold += .0021*math.sin(theta*15+w*17)*math.sin(w*math.pi)
    rx = .147+.080*w+fold
    ry = .139+.102*w+fold
    x = rx*math.sin(theta)
    y = -ry*math.cos(theta)+.005
    z = 1.858-.151*w-.061*front**2*math.sin(w*math.pi*.8)
    z += .013*math.sin(theta*1.0+.4)+.008*math.sin(theta*3+w*4)
    z += .0045*math.sin(theta*9+2*w)*(w*.6+.4)
    z += .0020*math.sin(theta*19-w*4)
    return (x,y,z)


def _cowl(plain, seam, collection):
    ns, nw = 192, 60
    vertices, uv, faces = [], [], []
    for j in range(nw+1):
        w=j/nw
        for i in range(ns+1):
            theta=i/ns*TAU
            vertices.append(_cowl_point(theta,w))
            uv.append((i/ns*2.8,w*.55))
    for j in range(nw):
        for i in range(ns):
            a=j*(ns+1)+i
            faces.append((a,a+ns+1,a+ns+2,a+1))
    obj=_mesh('Elite_Cowl | asymmetrical gathered wool folds',vertices,faces,
              uv,plain,collection,.003)
    paths=[[_cowl_point(i/ns*TAU,w) for i in range(ns+1)] for w in [0.005,.995]]
    edge=_curves('Elite_Cowl | rolled hand-sewn hems',paths,seam,collection,.0012)
    return [obj,edge]


def _tabard(material, seam, collection):
    objects=[]
    # Slit front panels frame, rather than obscure, the decorated thigh plates.
    for sign in [-1,1]:
        nu,nv=40,160
        vertices,uv,faces=[],[],[]
        for j in range(nv+1):
            v=j/nv
            for i in range(nu+1):
                u=i/nu
                edge_wear=(.0034*math.sin(v*79+sign)
                           +.0020*math.sin(v*157))*v*v
                width=.104-.015*v+.008*math.sin(v*5)+edge_wear
                center=sign*(.059+.011*v)+.009*math.sin(v*5+sign)*v
                x=center+(u-.5)*width
                hem=(.35 if sign<0 else .485)
                hem+=.035*math.sin(u*TAU*1.7+sign)+.012*math.sin(u*TAU*8.7)
                for location,depth,spread in [(.22,.064,.071),(.64,.085,.081),(.86,.04,.048)]:
                    hem+=depth*max(0,1-abs(u-location)/spread)
                z=1.23*(1-v)+hem*v
                # One broad, shallow drape; no longitudinal tubular ridges.
                y=-.257-.007*math.sin(v*5)+.0028*math.cos(u*math.pi+v*2)
                y+=.020*v*v+.0020*math.sin(u*7+v*19)*v*v
                vertices.append((x,y,z))
                uv.append((u*.26+(0 if sign<0 else .5),1-v*.64))
        for j in range(nv):
            for i in range(nu):
                u,v=(i+.5)/nu,(j+.5)/nv
                hole=False
                for cx,cy,rx,ry in [(.27,.70,.075,.023),(.73,.84,.09,.034),
                                    (.37,.935,.10,.048),(.67,.59,.035,.012)]:
                    wobble=.15*math.sin(u*99+v*73)
                    if (u-cx)**2/rx**2+(v-cy)**2/ry**2<1+wobble:
                        hole=True
                # Open tears break the edge silhouette as well as the surface.
                slit=.024+.085*max(0,(v-.84)/.16)
                if (v>.84 and abs(u-(.53+.015*math.sin(v*38)))<slit
                        or v>.90 and u<.05+.02*math.sin(v*84)):
                    hole=True
                if hole:
                    continue
                a=j*(nu+1)+i
                faces.append((a,a+nu+1,a+nu+2,a+1))
        objects.append(_mesh('Elite_Tabard_%s | split ragged front wool'%('L' if sign<0 else 'R'),
                             vertices,faces,uv,material,collection,.0018))
        rng=random.Random(501+sign)
        paths=[]
        for i in range(1,nu):
            u=i/nu
            if u<.075 or abs(u-(.53+.015*math.sin(38)))<.111:
                continue
            start=Vector(vertices[nv*(nu+1)+i])
            paths.append([tuple(start),tuple(start+Vector((rng.uniform(-.003,.003),-.001,-rng.uniform(.007,.021))))])
        objects.append(_curves('Elite_Tabard_%s | unravelled ends'%sign,paths,
                               seam,collection,.00048))
    return objects


def build_textiles(collection):
    """Build cloth into a supplied Blender collection; return created objects.

    The caller owns scene/export setup. Curves remain editable and should be
    converted to meshes by the caller before glTF export if required. Cloth
    modifiers should be evaluated for final export to preserve thickness.
    """
    material,plain,seam,embroidery=_materials()
    objects=_cape(material,seam,embroidery,collection)
    objects.extend(_cowl(plain,seam,collection))
    objects.extend(_tabard(material,seam,collection))
    return objects
