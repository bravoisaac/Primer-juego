"""Local, reproducible modelling of the siege elite. No remote generation.

Run with Blender --background --python this_file.py [-- --draft].
The supplied normal paladin is retained as a textured anatomical underlayer;
all elite plates, helmet, filigree, fastenings and textiles are authored here.
"""
from __future__ import annotations

import json
import math
import sys
import shutil
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from elite_ornament import create_materials, decorate_panel
from elite_textiles import build_textiles

OUT = ROOT / 'Assets/Characters/Enemies/PaladinElite'
BASE = ROOT / 'Assets/Characters/Enemies/Paladin/Source/PaladinSoldier_Meshy_Source.glb'
REFERENCE = Path(r'C:\Users\isaac\Downloads\Paladín oscuro de asedio en cuatro vistas Elite.png')
DRAFT = '--draft' in sys.argv
TAU = math.tau
PI = math.pi
M = {}
C = {}


def collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def put(obj, name, mat, col='armor'):
    obj.name = name
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    C[col].objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    return obj


def mesh(name, vertices, faces, mat, col='armor', uv=None):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    C[col].objects.link(obj)
    if mat:
        data.materials.append(mat)
    if uv:
        layer = data.uv_layers.new(name='UVMap')
        for poly in data.polygons:
            for li in poly.loop_indices:
                layer.data[li].uv = uv[data.loops[li].vertex_index]
    for face in data.polygons:
        face.use_smooth = True
    return obj


def curve(name, lines, radius, mat, col='detail'):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = 1
    data.bevel_depth = radius
    data.bevel_resolution = 2
    for line in lines:
        spline = data.splines.new('POLY')
        spline.points.add(len(line)-1)
        for p, co in zip(spline.points, line):
            p.co = (*co, 1)
    obj = bpy.data.objects.new(name, data)
    C[col].objects.link(obj)
    data.materials.append(mat)
    return obj


def surface(name, fn, mat=None, nu=48, nv=32, thickness=.005, trim=True,
            ornate=False, rivets=False, col='armor', flip=False):
    vs, uvs, faces = [], [], []
    for j in range(nv+1):
        for i in range(nu+1):
            u, v = i/nu, j/nv
            vs.append(fn(u, v))
            uvs.append((u, v))
    for j in range(nv):
        for i in range(nu):
            a=j*(nu+1)+i
            face=(a,a+1,a+nu+2,a+nu+1)
            faces.append(tuple(reversed(face)) if flip else face)
    obj=mesh(name, vs, faces, mat or M['steel'], col, uvs)
    if thickness:
        mod=obj.modifiers.new('Forged plate thickness', 'SOLIDIFY')
        mod.thickness=thickness
        mod.offset=-1
    if trim:
        lines=[[fn(i/80,0) for i in range(81)], [fn(i/80,1) for i in range(81)],
               [fn(0,i/60) for i in range(61)], [fn(1,i/60) for i in range(61)]]
        curve(name+'_RolledBrassEdge',lines,.0028,M['gold'])
        curve(name+'_InsetScribe',[[fn(i/80,.032) for i in range(81)],
                                  [fn(i/80,.968) for i in range(81)]],.00065,M['black'])
    if ornate:
        chased(name,fn)
    if rivets:
        for u in (.08,.25,.42,.58,.75,.92):
            for v in (.045,.955):
                rivet(name+'_Rivet',fn(u,v),.0043)
    return obj


def chased(name,fn,tiles=(2,2),flip=False):
    """Fine foliate inlay follows the plate normal, including domed panels."""
    def lifted(u,v):
        p=Vector(fn(u,v))
        du=Vector(fn(min(1,u+.0001),v))-Vector(fn(max(0,u-.0001),v))
        dv=Vector(fn(u,min(1,v+.0001)))-Vector(fn(u,max(0,v-.0001)))
        normal=du.cross(dv).normalized()
        return p+normal*(-.001 if flip else .001)
    for x in range(tiles[0]):
        for y in range(tiles[1]):
            def patch(u,v,x=x,y=y):
                return lifted((x+.035+.93*u)/tiles[0],(y+.035+.93*v)/tiles[1])
            made=decorate_panel(f'{name}_Inlay_{x}_{y}',patch,C['detail'],M['gold'],M['black'],density=1.6)
            for obj in made:
                obj.data.bevel_depth*=.65


def sphere(name, loc, scale, mat, col='detail', segments=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=10, location=loc)
    obj=put(bpy.context.object,name,mat,col)
    obj.scale=scale
    for p in obj.data.polygons:
        p.use_smooth=True
    return obj


def rivet(name, loc, radius=.004):
    return sphere(name,loc,(radius,radius*.58,radius),M['gold'])


def medallion(name,center,radius):
    c=Vector(center)
    sphere(name+'_Boss',c,(radius,.012,radius),M['gold'],segments=32)
    sphere(name+'_DarkInset',c+Vector((0,-.011,0)),(radius*.82,.005,radius*.82),M['dark_steel'],segments=32)
    lines=[]
    for k in range(8):
        a=k*TAU/8
        lines.append([c+Vector((math.sin(a)*radius*t,-.017-math.sin(PI*t)*.008,math.cos(a)*radius*t)) for t in (0,.3,.7,.86)])
    lines.append([c+Vector((math.sin(a*TAU/64)*radius*.89,-.015,math.cos(a*TAU/64)*radius*.89)) for a in range(65)])
    curve(name+'_Sunburst',lines,.0018,M['gold'])
    rivet(name+'_CentralStud',c+Vector((0,-.025,0)),radius*.16)


def sleeve_fn(top,bottom,r_top,r_bottom,depth=1,arc=2.8):
    top,bottom=Vector(top),Vector(bottom)
    axis=(top-bottom).normalized()
    side=Vector((1,0,0))
    side=(side-axis*side.dot(axis)).normalized()
    front=axis.cross(side)
    if front.y>0:
        front=-front
    def fn(u,v):
        a=(u-.5)*arc
        r=r_bottom+(r_top-r_bottom)*v
        r*=1+.035*math.cos(a*8)*math.sin(PI*v)
        return bottom.lerp(top,v)+side*(math.sin(a)*r)+front*(math.cos(a)*r*depth)
    return fn


def import_underlayer():
    bpy.ops.import_scene.gltf(filepath=str(BASE))
    objs=[o for o in bpy.context.selected_objects if o.type=='MESH']
    corners=[o.matrix_world@Vector(c) for o in objs for c in o.bound_box]
    mn=Vector(tuple(min(c[i] for c in corners) for i in range(3)))
    mx=Vector(tuple(max(c[i] for c in corners) for i in range(3)))
    sc=2.08/(mx.z-mn.z)
    center=(mn+mx)*.5
    for obj in objs:
        matworld=obj.matrix_world.copy()
        for vert in obj.data.vertices:
            p=matworld@vert.co
            p=Vector(((p.x-center.x)*sc,(p.y-center.y)*sc,(p.z-mn.z)*sc))
            # Anatomical body broadened, feet grounded. Arm warp is reversible
            # in the untouched source and explicitly not an animation rig.
            side=1 if p.x>=0 else -1
            ax=abs(p.x)
            if p.z>1.37 and ax>.24:
                t=max(0,min(1,(ax-.24)/.11))
                t=t*t*(3-2*t)
                angle=math.radians(67)*t
                dx=ax-.28+max(0,ax-.42)*.52
                dz=p.z-1.64
                p.x=side*(.325+dx*math.cos(angle)+dz*math.sin(angle))
                p.z=1.69-dx*math.sin(angle)+dz*math.cos(angle)
            else:
                p.x*=1.16 if p.z>1.05 else .94
            p.y*=1.12
            vert.co=p
        obj.matrix_world.identity()
        # Replace the original helmet with a separately built elite helmet.
        import bmesh
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.delete(bm,geom=[v for v in bm.verts if (v.co.z>1.825 and abs(v.co.x)<.22)
                                or (v.co.z<1.095 and abs(v.co.x)>.405)],context='VERTS')
        bm.to_mesh(obj.data);bm.free()
        put(obj,'Paladin_Normal_Reposed_Underlayer',None,'base')
        obj['provenance']='User supplied normal paladin GLB, CC BY 4.0 per project record'
        obj['pose']='Static geometric repose, no skeleton or skinning'
        for polygon in obj.data.polygons:
            polygon.use_smooth=True
    return objs


def cuirass():
    def chest(u,v):
        a=(u-.5)*2.65
        width=.238+.060*math.sin(v*PI*.70)
        depth=.179+.044*math.sin(v*PI*.83)
        x=width*math.sin(a)
        y=-depth*math.cos(a)-.009*math.exp(-a*a*24)
        z=1.25+.46*v-.065*(1-v)*(math.cos(a)**4)-.045*v*(math.sin(a)**2)
        # Subtle fluting, not surface noise.
        y-=.0028*math.cos(a*18)*math.sin(PI*v)**2
        return Vector((x,y,z))
    surface('Cuirass_MainForging',chest,nu=100,nv=64,rivets=True)
    chased('Cuirass_MainChasing',chest,tiles=(2,2))
    curve('Cuirass_MedianKeel',[[chest(.5,v/100)+Vector((0,-.002,0)) for v in range(101)]],.003,M['gold'])
    # Curved nested breast ribs and heraldic chest emblem.
    ribs=[]
    for side in (-1,1):
        for j in range(3):
            ribs.append([chest(.5+side*(.06+.36*t),.75-j*.105-.18*math.sin(t*PI*.8)) + Vector((0,-.002,0)) for t in [k/60 for k in range(61)]])
    curve('Cuirass_ChasedBreastRibs',ribs,.0017,M['gold'])
    medallion('Ocaso_HeartSeal',(0,-.243,1.50),.037)
    for j in range(3):
        lo=1.12+j*.055
        def fauld(u,v,lo=lo,j=j):
            a=(u-.5)*2.85
            r=.245+j*.004
            return Vector((r*math.sin(a),-(.172+j*.004)*math.cos(a),lo+.081*v-.025*math.cos(a)))
        surface(f'Waist_ArticulatedLame_{j+1}',fauld,nu=64,nv=10,rivets=True)
    # Substantial leather belt with stitched edges and separate rectangular buckle.
    def belt(u,v):
        a=u*TAU
        return Vector((.256*math.sin(a),-.185*math.cos(a),1.185+.049*v+.022*math.sin(a)))
    surface('Belt_Leather',belt,M['leather'],nu=96,nv=8,trim=False,thickness=.004)
    stitches=[]
    for k in range(150):
        for v in (.14,.86):
            stitches.append([belt((k+.12)/150,v),belt((k+.6)/150,v)])
    curve('Belt_Stitches',stitches,.00065,M['gold'])
    curve('Belt_Buckle',[[(-.038,-.198,1.181),(.038,-.198,1.181),(.038,-.198,1.242),(-.038,-.198,1.242),(-.038,-.198,1.181)],[(0,-.207,1.187),(0,-.207,1.235)]],.004,M['gold'])


def pauldrons_and_arms():
    for side in (-1,1):
        label='L' if side>0 else 'R'
        def dome(u,v,side=side):
            a=u*TAU
            t=.035+v*1.53
            return Vector((side*.336+.226*math.sin(t)*math.cos(a),.212*math.sin(t)*math.sin(a),1.636+.211*math.cos(t)))
        surface(f'{label}_Pauldron_DomedMantle',dome,nu=112,nv=48,trim=False,thickness=.008,flip=True)
        curve(f'{label}_Pauldron_RolledRim',[[dome(i/120,1) for i in range(121)]],.0044,M['gold'])
        curve(f'{label}_Pauldron_InnerRim',[[dome(i/120,.935) for i in range(121)]],.0011,M['gold'])
        for i in range(22):
            rivet(f'{label}_Pauldron_Rivet',dome(i/22,.967),.005)
        for segment in range(4):
            def ornament(u,v,segment=segment):
                return dome((segment+u)/4,.16+v*.79)
            chased(f'{label}_Pauldron_FoliateChasing_{segment}',ornament,tiles=(1,1),flip=True)
        # Real overlapping plates step from the shoulder to the elbow.
        for j in range(4):
            top=(side*(.361+j*.026),0,1.653-j*.068)
            bottom=(side*(.387+j*.024),-.008,1.542-j*.068)
            fn=sleeve_fn(top,bottom,.171-j*.016,.158-j*.015,depth=.96,arc=6.18)
            surface(f'{label}_UpperArm_Lame_{j+1}',fn,nu=64,nv=14,rivets=True)
        elbow=(side*.466,-.019,1.323)
        sphere(f'{label}_Elbow_Articulation',elbow,(.100,.094,.089),M['dark_steel'],'armor',24)
        fn=sleeve_fn((side*.48,-.016,1.374),(side*.492,-.035,1.283),.108,.092,arc=3.3)
        surface(f'{label}_Elbow_Couter',fn,nu=40,nv=24,ornate=True)
        fn=sleeve_fn((side*.49,-.025,1.299),(side*.512,-.041,1.061),.112,.079,depth=1.07,arc=6.18)
        surface(f'{label}_Vambrace_Forged',fn,nu=72,nv=44,ornate=True,rivets=True)
        for k,z in enumerate((1.08,1.245)):
            band=sleeve_fn((side*.506,-.032,z+.023),(side*.508,-.035,z-.014),.091 if k==0 else .11,.088 if k==0 else .107,arc=5.9)
            surface(f'{label}_Vambrace_Binding_{k}',band,M['leather'],nu=60,nv=6)
        medallion(f'{label}_MantleClasp',(side*.257,-.185,1.716),.036)


def gauntlets():
    """Separate cupped steel gauntlets, with individual articulated fingers."""
    for side in (-1,1):
        label='L' if side>0 else 'R'
        cx=side*.512
        sphere(f'{label}_Glove_LeatherPalm',(cx,-.051,1.018),(.049,.038,.068),M['leather'],'armor',24)
        fn=sleeve_fn((cx,-.052,1.076),(cx,-.067,.988),.052,.048,depth=.86,arc=3.65)
        surface(f'{label}_Gauntlet_MetacarpalPlate',fn,nu=40,nv=30)
        chased(f'{label}_Gauntlet_ChasedSun',fn,tiles=(1,1))
        for finger in range(4):
            x=cx+side*(finger-1.5)*.023
            dz=(.005,-.004,0,.018)[finger]
            points=[(x,-.087,.992+dz),(x,-.116,.969+dz),(x,-.115,.939+dz),(x,-.091,.928+dz)]
            sphere(f'{label}_Knuckle_{finger}',points[0],(.015,.017,.016),M['steel'],'armor')
            for seg in range(3):
                top,bottom=Vector(points[seg]),Vector(points[seg+1])
                sphere(f'{label}_FingerJoint_{finger}_{seg}',bottom,(.010,.011,.011),M['dark_steel'],'armor')
                fn=sleeve_fn(top,bottom,.012-seg*.001,.011-seg*.001,depth=1,arc=5.7)
                surface(f'{label}_FingerPlate_{finger}_{seg}',fn,nu=20,nv=7,thickness=.0015,trim=False)
                curve(f'{label}_FingerHinge_{finger}_{seg}',[[fn(i/24,.12) for i in range(25)]],.00085,M['gold'])
            sphere(f'{label}_FingerTip_{finger}',points[-1],(.009,.010,.011),M['steel'],'armor')
        thumb=[(cx-side*.047,-.060,1.030),(cx-side*.063,-.095,1.008),(cx-side*.057,-.128,.982)]
        for seg in range(2):
            sphere(f'{label}_ThumbJoint_{seg}',thumb[seg],(.018,.019,.020),M['dark_steel'],'armor')
            fn=sleeve_fn(thumb[seg],thumb[seg+1],.018,.015,depth=.95,arc=5.6)
            surface(f'{label}_ThumbPlate_{seg}',fn,nu=24,nv=10,thickness=.002,trim=False)
        sphere(f'{label}_ThumbTip',thumb[-1],(.014,.017,.017),M['steel'],'armor')


def tassets_and_legs():
    for side in (-1,1):
        label='L' if side>0 else 'R'
        def tasset(u,v,side=side):
            w=.123-.027*v
            x=side*(.162+.043*(1-v))+(u-.5)*2*w
            y=-.185-.044*math.sin(PI*v)-.033*(1-v)+.035*((u-.5)*2)**2
            z=.803+.334*v+.025*((u-.5)*2)**2
            return Vector((x,y,z))
        surface(f'{label}_Tasset_EngravedShield',tasset,nu=56,nv=60,ornate=True,rivets=True)
        for j in range(2):
            def latch(u,v,j=j):
                return tasset(u,.83+j*.081+v*.069)+Vector((0,-.007,0))
            surface(f'{label}_Tasset_Suspension_{j}',latch,nu=56,nv=8,rivets=True)
        for j in range(2):
            fn=sleeve_fn((side*.18,.008,.846-j*.072),(side*.181,.008,.745-j*.072),.124,.114,depth=1.05,arc=3.0)
            surface(f'{label}_Thigh_Lame_{j}',fn,nu=50,nv=10,rivets=True)
        # Pointed knee cop, convex rather than a flat badge.
        def knee(u,v,side=side):
            a=(u-.5)*PI
            w=.11*(.55+.45*math.sin(PI*v))
            return Vector((side*.181+w*math.sin(a),-.13-.063*math.sin(PI*v)*math.cos(a),.535+.205*v+.035*abs(math.sin(a))*(.5-v)))
        surface(f'{label}_Knee_GothicCop',knee,nu=52,nv=40,ornate=True)
        medallion(f'{label}_Knee_SunSeal',(side*.181,-.197,.638),.029)
        def greave(u,v,side=side):
            a=(u-.5)*6.18
            radius=.070+.032*v+.016*math.sin(PI*v)
            x=side*(.19-.006*v)+radius*math.sin(a)
            y=.058-(.082+.037*v)*math.cos(a)-.012*math.exp(-a*a*16)
            z=.16+.389*v+.012*math.cos(a)*(1-v)
            return Vector((x,y,z))
        surface(f'{label}_Greave_Fluted',greave,nu=68,nv=64,ornate=True,rivets=True)
        curve(f'{label}_Greave_Keel',[[greave(.5,i/80)+Vector((0,-.002,0)) for i in range(81)]],.0025,M['gold'])
        for j in range(4):
            z=.157+j*.032
            fn=sleeve_fn((side*.21,.036,z+.025),(side*.21,.030,z-.025),.077+j*.003,.083+j*.003,depth=1.25,arc=3.5)
            surface(f'{label}_Ankle_Lame_{j}',fn,nu=48,nv=8,rivets=j==0)
        # Curved sabaton scales follow the instep to the toe.
        for j in range(5):
            def toe(u,v,j=j,side=side):
                a=(u-.5)*PI
                y=-.248+j*.043+v*.055
                width=.070+.017*math.sin((j/6)*PI)
                z=.037+j*.014+.025*math.cos(a)
                return Vector((side*.22+width*math.sin(a),y+.012,z+.008*math.sin(v*PI)))
            surface(f'{label}_Sabaton_ArticulatedToe_{j}',toe,nu=32,nv=12)


def helmet():
    rings=[(1.815,.107,.125),(1.935,.137,.152),(2.026,.142,.150),(2.090,.115,.124),(2.165,.014,.019),(2.181,.002,.003)]
    n=16
    vs=[];uv=[];fs=[]
    for j,(z,rx,ry) in enumerate(rings):
        for i in range(n+1):
            a=i*TAU/n
            vs.append((rx*math.sin(a),-ry*math.cos(a),z))
            uv.append((i/n,j/(len(rings)-1)))
    for j in range(len(rings)-1):
        for i in range(n):
            a=j*(n+1)+i
            fs.append((a,a+1,a+n+2,a+n+1))
    obj=mesh('Helm_FacetedSkull',vs,fs,M['dark_steel'],uv=uv)
    for p in obj.data.polygons:p.use_smooth=False
    mod=obj.modifiers.new('Hammered edge bevels','BEVEL');mod.width=.002;mod.segments=3
    seams=[]
    for i in range(0,n,2):
        a=i*TAU/n
        seams.append([(rx*math.sin(a)*1.012,-ry*math.cos(a)*1.012,z) for z,rx,ry in rings[1:]])
    curve('Helm_RadialBrassSeams',seams,.0019,M['gold'])
    for facet in range(8):
        def crest_panel(u,v,facet=facet):
            a=(facet+u)*TAU/8
            z=2.033+.130*v
            lo=next(i for i in range(len(rings)-1) if rings[i][0]<=z<=rings[i+1][0])
            t=(z-rings[lo][0])/(rings[lo+1][0]-rings[lo][0])
            rx=rings[lo][1]*(1-t)+rings[lo+1][1]*t
            ry=rings[lo][2]*(1-t)+rings[lo+1][2]*t
            f=a*n/TAU; a0=math.floor(f)*TAU/n; a1=a0+TAU/n; f=f-math.floor(f)
            return Vector((rx*(math.sin(a0)*(1-f)+math.sin(a1)*f),-ry*(math.cos(a0)*(1-f)+math.cos(a1)*f),z))
        chased(f'Helm_CrownChasing_{facet}',crest_panel,tiles=(1,1))
    def mask(u,v):
        a=(u-.5)*2.18
        rx=.113+.025*v
        ry=.139+.025*v
        return Vector((rx*math.sin(a),-ry*math.cos(a)-.018*math.exp(-a*a*25),1.83+.162*v+.031*(1-v)*abs(math.sin(a))))
    surface('Visor_EngravedLowerBevor',mask,nu=72,nv=44,ornate=True,rivets=False)
    def brow(u,v):
        a=(u-.5)*2.73
        return Vector(((.147-.009*v)*math.sin(a),-(.163-.013*v)*math.cos(a),2.009+.058*v+.008*math.cos(a)))
    surface('Visor_BrowPlate',brow,nu=72,nv=18,ornate=True,rivets=True)
    # Narrow dark ocular aperture and the two curved eye openings.
    fn=lambda u,v:Vector((.143*math.sin((u-.5)*2.5),-.161*math.cos((u-.5)*2.5),1.994+.015*v))
    surface('Visor_OcularShadow',fn,M['black'],nu=64,nv=4,thickness=.002,trim=False)
    vents=[]
    for side in (-1,1):
        for j in range(5):
            u=.5+side*(.16+j*.043)
            vents.append([mask(u,.37+t*.14)+Vector((0,-.002,0)) for t in (0,.25,.75,1)])
        sphere('Visor_PivotBolt',(side*.137,-.033,2.0),(.008,.009,.009),M['gold'])
    curve('Visor_BreathingEtch',vents,.0017,M['black'])
    # Raised central crest climbs to the peaked crown.
    curve('Helm_CentralCrest',[[(0,-.164,2.069),(0,-.132,2.10),(0,-.088,2.139),(0,-.02,2.179)]],.0035,M['gold'])


def look_at(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()


def presentation():
    scene=bpy.context.scene
    world=bpy.data.worlds.new('Elite_StudioWorld');scene.world=world;world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.18,.21,1)
    world.node_tree.nodes['Background'].inputs[1].default_value=.36
    floor_mat=bpy.data.materials.new('Studio_Charcoal');floor_mat.diffuse_color=(.025,.033,.042,1);floor_mat.use_nodes=True
    floor_mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.025,.033,.042,1)
    floor_mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.76
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.018));put(bpy.context.object,'StudioFloor',floor_mat,'studio')
    for name,loc,power,color,size in [
        ('Key',(-3,-4,4.5),620,(1,.84,.68),3.3),
        ('Fill',(3,-1.8,2.5),400,(.68,.79,1),2.8),
        ('Rim',(1.3,2.5,3.6),850,(1,.83,.63),2),
        ('Top',(-1,1,5),300,(.78,.87,1),2),
    ]:
        bpy.ops.object.light_add(type='AREA',location=loc)
        obj=put(bpy.context.object,name,None,'studio');obj.data.energy=power;obj.data.color=color;obj.data.shape='DISK';obj.data.size=size
        look_at(obj,(0,0,1.2))
    bpy.ops.object.camera_add(location=(3,-5,2.85))
    cam=put(bpy.context.object,'Camera_Elite_Portrait',None,'studio');cam.data.type='ORTHO';cam.data.ortho_scale=2.48
    look_at(cam,(0,0,1.10));scene.camera=cam
    scene.render.engine='CYCLES'
    scene.cycles.samples=24 if DRAFT else 64
    scene.cycles.use_denoising=True
    try:
        preferences=bpy.context.preferences.addons['cycles'].preferences
        preferences.compute_device_type='OPTIX';preferences.get_devices()
        for device in preferences.devices: device.use=device.type!='CPU'
        scene.cycles.device='GPU'
    except Exception:scene.cycles.device='CPU'
    scene.render.resolution_x=850 if DRAFT else 1500
    scene.render.resolution_y=1100 if DRAFT else 1900
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.view_settings.view_transform='AgX'
    scene.view_settings.look='AgX - Medium High Contrast'
    scene.render.film_transparent=False
    return cam


def configure_source_view():
    """Open the editable file on a clean material preview of the character."""
    bpy.ops.object.select_all(action='DESELECT')
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                space=area.spaces.active
                space.shading.type='MATERIAL'
                space.shading.use_scene_world=False
                space.shading.use_scene_lights=False
                space.overlay.show_overlays=False
                space.region_3d.view_perspective='CAMERA'
                space.region_3d.view_camera_zoom=0


def save_export():
    scene=bpy.context.scene
    asset=[o for k,c in C.items() if k!='studio' for o in c.objects if o.type in {'MESH','CURVE'}]
    for obj in asset:
        obj['asset_family']='TenFe / PaladinElite / Siege'
    # Keep explicit texture sources as well as packed copies in the deliverables.
    for im in list(bpy.data.images):
        if im.name in {'Render Result','Viewer Node'} or not im.has_data:
            continue
        safe_name=''.join(c if c.isalnum() or c in '._-' else '_' for c in im.name)
        im.filepath_raw=str(OUT/'Textures'/f'{safe_name}.png')
        im.file_format='PNG'
        im.save()
        im.pack()
    # Keep the source editable and package every texture.
    bpy.ops.file.pack_all()
    configure_source_view()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Source/PaladinElite.blend'))
    if DRAFT:return
    for obj in asset:obj.select_set(True)
    bpy.context.view_layer.objects.active=asset[0]
    bpy.ops.object.convert(target='MESH')
    export_objects=list(bpy.context.selected_objects)
    # Ensure ornaments get valid UVs. Their thin, nearly solid metal surface
    # still exports correctly when flat-mapped; plate UVs are authored above.
    for obj in export_objects:
        if not obj.data.uv_layers:
            layer=obj.data.uv_layers.new(name='UVMap')
            for poly in obj.data.polygons:
                for li in poly.loop_indices:
                    co=obj.data.vertices[obj.data.loops[li].vertex_index].co
                    layer.data[li].uv=(co.x*4,co.z*4)
    bpy.ops.export_scene.gltf(filepath=str(OUT/'Exports/PaladinElite.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True)
    bpy.ops.export_scene.fbx(filepath=str(OUT/'Exports/PaladinElite.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Y',axis_up='Z',path_mode='COPY',embed_textures=True,bake_anim=False)
    stats={'asset':'PaladinElite','method':'Local Blender modelling over user supplied normal paladin','rigged':False,'animations':0,'objects':len(export_objects),'vertices':sum(len(o.data.vertices) for o in export_objects),'materials':sorted({s.material.name for o in export_objects for s in o.material_slots if s.material}),'limitations':['Static presentation pose, no rig or skin weights','Dense presentation geometry; requires retopology and game LODs','Procedural interpretation of reference; not an exact reconstruction']}
    triangles=0
    for obj in export_objects:obj.data.calc_loop_triangles();triangles+=len(obj.data.loop_triangles)
    stats['triangles']=triangles
    coords=[o.matrix_world@Vector(c) for o in export_objects for c in o.bound_box]
    stats['dimensions_m']=[max(c[i] for c in coords)-min(c[i] for c in coords) for i in range(3)]
    (OUT/'validation_elite.json').write_text(json.dumps(stats,indent=2,ensure_ascii=False),encoding='utf-8')
    print('ELITE_VALIDATION='+json.dumps(stats))


def main():
    for d in ('Source','Exports','Preview','References','Textures'):(OUT/d).mkdir(parents=True,exist_ok=True)
    if REFERENCE.exists():shutil.copy2(REFERENCE,OUT/'References/PaladinElite_FourViews.png')
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for key,name in [('base','00_NormalPaladin_Underlayer'),('armor','01_EliteForgedArmor'),('detail','02_EngravingsAndFasteners'),('textile','03_Textiles'),('studio','90_Studio')]:C[key]=collection(name)
    M.update(create_materials())
    print('ELITE_STEP=import_base',flush=True);import_underlayer()
    print('ELITE_STEP=cuirass',flush=True);cuirass()
    print('ELITE_STEP=arms',flush=True);pauldrons_and_arms()
    print('ELITE_STEP=gauntlets',flush=True);gauntlets()
    print('ELITE_STEP=legs',flush=True);tassets_and_legs()
    print('ELITE_STEP=helmet',flush=True);helmet()
    print('ELITE_STEP=textiles',flush=True);build_textiles(C['textile'])
    cam=presentation()
    print('ELITE_STEP=save_export',flush=True);save_export()
    for title,loc,target,scale in [
        ('PaladinElite_Front',(3,-5,2.6),(0,0,1.10),2.47),
        ('PaladinElite_Back',(-3,5,2.7),(0,0,1.09),2.47),
        ('PaladinElite_Detail',(2.7,-5,2.5),(0,-.03,1.69),1.18),
    ][:1 if DRAFT else 3]:
        cam.location=loc;look_at(cam,target);cam.data.ortho_scale=scale
        bpy.context.scene.render.filepath=str(OUT/f'Preview/{title}.png')
        print('ELITE_STEP=render_'+title,flush=True);bpy.ops.render.render(write_still=True)
    print('ELITE_COMPLETE',flush=True)


if __name__=='__main__':main()
