"""Clean local form study, derived non-destructively from PaladinElite.blend.

No remote services. Preserve the detailed source and all game assets.
Run with Blender --background --factory-startup --python-exit-code 1 --python ...
"""
import bpy
import math
import json
import sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
import create_paladin_elite as shapes
OUT=ROOT/'Assets/Characters/Enemies/PaladinElite/Base'
SOURCE=OUT.parent/'Source/PaladinElite.blend'
TAU=math.tau


def material(name,color,roughness=.65):
    mat=bpy.data.materials.new(name);mat.diffuse_color=(*color,1);mat.use_nodes=True
    nodes=mat.node_tree.nodes;nodes.clear()
    shader=nodes.new('ShaderNodeBsdfPrincipled')
    shader.inputs['Base Color'].default_value=(*color,1)
    shader.inputs['Roughness'].default_value=roughness
    shader.inputs['Metallic'].default_value=.05
    out=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(shader.outputs['BSDF'],out.inputs['Surface'])
    return mat


def assign(obj,mat):
    obj.data.materials.clear();obj.data.materials.append(mat)
    for p in obj.data.polygons:p.material_index=0


def panel(name,fn,mat=None,nu=40,nv=28,thickness=.006,flip=False):
    return shapes.surface(name,fn,mat or ARMOR,nu,nv,thickness,False,False,False,'armor',flip)


def simplify_source_armor():
    with bpy.data.libraries.load(str(SOURCE),link=False) as (src,dst):
        dst.collections=['01_EliteForgedArmor']
    col=dst.collections[0];bpy.context.scene.collection.children.link(col)
    col.name='01_Placas_base_editables';shapes.C['armor']=col
    # Appended objects need dependency evaluation before baking matrix_world.
    bpy.context.view_layer.update()
    removed=[]
    for obj in list(col.objects):
        if any(x in obj.name for x in ('Helm_','Visor_','Sabaton_')):
            removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True);continue
        if obj.type!='MESH':continue
        # Bake object placement only; preserve plate thickness modifiers.
        mx=obj.matrix_world.copy()
        for vertex in obj.data.vertices:vertex.co=mx@vertex.co
        obj.matrix_world.identity()
        name=obj.name
        for vertex in obj.data.vertices:
            p=vertex.co
            if 'Pauldron_DomedMantle' in name:
                side=1 if p.x>0 else -1
                p.x=side*.316+(p.x-side*.336)*.86
                p.z=1.638+(p.z-1.636)*.80
                p.y*=.92
            elif any(x in name for x in ('UpperArm','Elbow','Vambrace','Glove','Gauntlet','Knuckle','Finger','Thumb')):
                p.x*=.90
            elif 'Cuirass' in name:
                t=max(0,min(1,(p.z-1.18)/.50));p.x*=.90+.10*t
                # Remove fluting: the base is only the large breastplate form.
            elif 'Waist' in name or 'Belt' in name:p.x*=.91
            elif 'Tasset' in name:p.y+=.025
            elif 'Knee' in name:p.y+=.025
        mat=DARK if any(x in name for x in ('Articulation','Joint','Leather','Binding')) else ARMOR
        assign(obj,mat)
        obj['stage']='Base forms; no engraving or decorative material'
        # Preserve regular quad boundaries: un-subdivide serrates plate hems.
    return removed


def padded_body():
    # A separate neutral mannequin replaces the noisy imported underlayer.
    def torso(u,v):
        a=u*TAU
        z=1.04+.65*v
        width=.197+.060*math.sin(v*math.pi*.72)
        depth=.134+.017*math.sin(v*math.pi)
        return Vector((width*math.sin(a),.018-depth*math.cos(a),z))
    obj=panel('Base_Cuerpo_bajo_armadura',torso,DARK,48,32,.008)
    for side in (-1,1):
        tag='L' if side>0 else 'R'
        for name,top,bottom,rt,rb in [
            ('Muslo',(side*.165,.030,1.095),(side*.177,.018,.634),.115,.093),
            ('Pantorrilla',(side*.180,.041,.646),(side*.206,.048,.137),.087,.063),
            ('Brazo',(side*.298,.022,1.699),(side*.423,-.018,1.321),.097,.074),
            ('Antebrazo',(side*.427,-.018,1.321),(side*.460,-.041,1.054),.078,.057),
        ]:
            fn=shapes.sleeve_fn(top,bottom,rt,rb,depth=.98,arc=TAU)
            panel(f'{tag}_Base_{name}',fn,DARK,32,18,.003)
        shapes.sphere(f'{tag}_Base_Rodilla',(side*.18,.015,.632),(.098,.112,.094),DARK,'armor',24)
        shapes.sphere(f'{tag}_Base_Cadera',(side*.132,.032,1.077),(.123,.128,.114),DARK,'armor',24)
        # Closed boots with a broad toe and a real flat sole.
        sections=[(-.255,.018,.038),(-.239,.069,.061),(-.180,.085,.084),
                  (-.085,.085,.125),(.010,.079,.167),(.085,.078,.125),(.130,.060,.102),(.145,.012,.074)]
        verts=[];faces=[];uv=[];n=32
        for j,(y,w,top) in enumerate(sections):
            for i in range(n):
                a=i*TAU/n
                z=.014+(top-.014)*(.5+.5*math.cos(a))
                verts.append((side*.21+w*math.sin(a),y,z));uv.append((i/n,j/(len(sections)-1)))
        for j in range(len(sections)-1):
            for i in range(n):
                k=j*n+i;kn=j*n+(i+1)%n
                faces.append((k,kn,kn+n,k+n))
        faces.extend((tuple(reversed(range(n))),tuple((len(sections)-1)*n+i for i in range(n))))
        shapes.mesh(f'{tag}_Base_Bota',verts,faces,DARK,uv=uv)
        def toe_guard(u,v,side=side):
            y=-.246+.265*v
            j=next(k for k in range(len(sections)-1) if sections[k][0]<=y<=sections[k+1][0])
            t=(y-sections[j][0])/(sections[j+1][0]-sections[j][0])
            w=sections[j][1]*(1-t)+sections[j+1][1]*t
            top=sections[j][2]*(1-t)+sections[j+1][2]*t
            a=(u-.5)*math.pi
            return Vector((side*.21+(w+.003)*math.sin(a),y,.014+(top-.014)*(.5+.5*math.cos(a))+.005))
        panel(f'{tag}_Bota_Cubierta_base',toe_guard,ARMOR,36,32,.003)
        shapes.sphere(f'{tag}_Base_Tobillo',(side*.207,.042,.165),(.066,.073,.107),DARK,'armor',24)


def helmet():
    # Curved cranium with a restrained sagittal crest, not a conical roof.
    profile=[(1.81,.104,.116),(1.87,.127,.142),(1.94,.144,.155),
             (2.013,.148,.160),(2.064,.133,.147),(2.105,.102,.115),
             (2.135,.056,.064),(2.162,.002,.002)]
    def skull(u,v):
        f=v*(len(profile)-1);j=min(int(f),len(profile)-2);t=f-j
        z,rx,ry=[profile[j][k]*(1-t)+profile[j+1][k]*t for k in range(3)]
        a=u*TAU
        return Vector((rx*math.sin(a),-ry*math.cos(a),z))
    panel('Casco_Calota_redondeada',skull,ARMOR,64,56,.007)
    def face(u,v):
        a=(u-.5)*2.37
        rx=.109+.040*v
        ry=.146+.020*v
        return Vector((rx*math.sin(a),-ry*math.cos(a)-.021*math.exp(-a*a*13),
                       1.823+.174*v+.055*(1-v)*abs(math.sin(a))))
    panel('Casco_Visor_sin_grabado',face,ARMOR,56,36,.007)
    def brow(u,v):
        a=(u-.5)*2.59
        return Vector(((.151-.013*v)*math.sin(a),-(.177-.017*v)*math.cos(a),2.011+.041*v+.006*math.cos(a)))
    panel('Casco_Frente_superior',brow,ARMOR,56,12,.006)
    panel('Casco_Ranura_ocular',lambda u,v:Vector((.149*math.sin((u-.5)*2.45),-.176*math.cos((u-.5)*2.45)-.001,1.998+.012*v)),DARK,48,4,.002)


def cloth():
    # Clean full fabric silhouettes; holes, trim and embroidery are deferred.
    def cape(u,v):
        width=.254+.172*v**.7
        hem=.32+.014*math.sin(u*TAU*2+.8)
        z=1.744*(1-v)+hem*v
        x=(2*u-1)*width
        y=.177+.164*v+.024*math.sin(v*math.pi*.8)*math.cos(u*TAU*5.5+.4*math.sin(v*4))
        y-=.050*abs(2*u-1)**4*(1-v)**4
        return Vector((x,y,z))
    panel('Tela_Capa_base_sin_bordado',cape,CLOTH,64,80,.002)
    def scarf(u,v):
        a=u*TAU;front=max(0,math.cos(a))
        fold=.007*math.sin(v*math.pi*5.7+.6*math.sin(a*2))
        x=(.145+.071*v+fold)*math.sin(a)
        y=-(.137+.096*v+fold)*math.cos(a)+.005
        z=1.853-.144*v-.039*front**2*math.sin(v*math.pi*.8)+.008*math.sin(a*3+v*2)
        return Vector((x,y,z))
    cowl=panel('Tela_Cuello_base',scarf,CLOTH,80,40,.002,flip=True)
    weld=cowl.modifiers.new('Close scarf seam','WELD');weld.merge_threshold=.00001
    bpy.context.view_layer.objects.active=cowl;bpy.ops.object.modifier_move_up(modifier=weld.name)
    for side in (-1,1):
        def tabard(u,v,side=side):
            x=side*.064+(u-.5)*.106
            z=1.18-(.66 if side>0 else .78)*v+.01*math.sin(u*math.pi)
            y=-.199-.040*v+.005*math.sin(u*TAU+v*3)*math.sin(v*math.pi)
            return Vector((x,y,z))
        panel(('L' if side>0 else 'R')+'_Tela_Faldon_base',tabard,CLOTH,24,56,.002,flip=True)


def studio():
    scene=bpy.context.scene
    scene.world=bpy.data.worlds.new('BaseStudioWorld');scene.world.use_nodes=True
    bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
    bg.inputs['Color'].default_value=(.20,.22,.25,1);bg.inputs['Strength'].default_value=.30
    floor=material('Estudio_suelo',(.042,.049,.057),.85)
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.013))
    shapes.put(bpy.context.object,'StudioFloor',floor,'studio')
    for name,loc,power,size in [('Key',(-3,-4,4),560,3),('Fill',(3,-1,2.8),320,3),('Rim',(1,3,3.2),650,2.5)]:
        bpy.ops.object.light_add(type='AREA',location=loc)
        o=shapes.put(bpy.context.object,name,None,'studio');o.data.energy=power;o.data.size=size
        shapes.look_at(o,(0,0,1.1))
    bpy.ops.object.camera_add(location=(2.6,-5,2.4))
    cam=shapes.put(bpy.context.object,'Camera_Base',None,'studio');cam.data.type='ORTHO';cam.data.ortho_scale=2.47
    shapes.look_at(cam,(0,0,1.08));scene.camera=cam
    scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
    try:
        pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
        for device in pref.devices:device.use=device.type!='CPU'
        scene.cycles.device='GPU'
    except Exception:scene.cycles.device='CPU'
    scene.render.resolution_x=1100;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
    scene.view_settings.look='AgX - Medium High Contrast'
    return cam


def export_and_validate():
    objects=list(shapes.C['armor'].objects)
    for obj in objects:
        obj['stage']='Base for silhouette approval; no rig or decorations'
    shapes.configure_source_view()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'PaladinElite_Base.blend'))
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.convert(target='MESH')
    objects=list(bpy.context.selected_objects)
    for obj in objects:
        if not obj.data.uv_layers:obj.data.uv_layers.new(name='BaseUV')
    bpy.ops.export_scene.gltf(filepath=str(OUT/'PaladinElite_Base.glb'),export_format='GLB',use_selection=True,export_apply=True)
    # Independent reload in a temporary scene verifies the actual deliverable.
    orig_scene=bpy.context.scene
    verify=bpy.data.scenes.new('Verification')
    bpy.context.window.scene=verify
    bpy.ops.import_scene.gltf(filepath=str(OUT/'PaladinElite_Base.glb'))
    imported=[o for o in verify.objects if o.type=='MESH']
    assert len(imported)==len(objects),'Mesh count changed across GLB round trip'
    assert not any(o.type in {'CAMERA','LIGHT'} for o in verify.objects),'Studio leaked into model'
    assert all(o.data.materials and o.data.uv_layers for o in imported),'Material or UV missing'
    triangles=0
    for obj in imported:
        obj.data.calc_loop_triangles();triangles+=len(obj.data.loop_triangles)
        assert all(math.isfinite(c) for v in obj.data.vertices for c in v.co),'Invalid vertex'
    bounds=[o.matrix_world@Vector(c) for o in imported for c in o.bound_box]
    dims=[max(c[i] for c in bounds)-min(c[i] for c in bounds) for i in range(3)]
    assert 2.0<dims[2]<2.3,f'Scale outside expected range: {dims}; tallest='+str(sorted([(o.name,o.dimensions.z) for o in imported],key=lambda x:x[1],reverse=True)[:5])
    mats={m for o in imported for m in o.data.materials}
    assert not any(n.type=='TEX_IMAGE' for m in mats for n in m.node_tree.nodes),'Base still has ornament textures'
    report={'status':'passed','mesh_objects':len(imported),'triangles':triangles,'dimensions_m':dims,
            'materials':sorted(m.name for m in mats),'image_textures':0,'ornamental_curves':0,
            'validation':'GLB reimport; meshes, UV, materials, finite geometry, scale, no studio/textures',
            'stage':'Static base-form study; not a rig or production retopology',
            'source_preserved':str(SOURCE)}
    (OUT/'validation_base.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    bpy.context.window.scene=orig_scene
    for obj in list(verify.objects):bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.scenes.remove(verify)
    print('BASE_VALIDATION='+json.dumps(report),flush=True)


def main():
    global ARMOR,DARK,CLOTH
    OUT.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ARMOR=material('Base_Armadura_gris',(.23,.245,.26),.64)
    DARK=material('Base_Articulaciones',(.105,.117,.13),.78)
    CLOTH=material('Base_Tela_neutra',(.18,.187,.196),.90)
    shapes.M.update(steel=ARMOR,dark_steel=DARK,black=DARK,leather=DARK,gold=ARMOR)
    shapes.C['detail']=shapes.collection('02_Sin_adornos')
    shapes.C['studio']=shapes.collection('90_Estudio')
    print('BASE_STEP=primary_shapes',flush=True);simplify_source_armor()
    print('BASE_STEP=anatomy_helmet_cloth',flush=True);padded_body();helmet();cloth()
    cam=studio()
    print('BASE_STEP=export',flush=True);export_and_validate()
    for title,loc in [('TresCuartos',(2.6,-5,2.4)),('Frente',(0,-6,1.22)),('Espalda',(-2.6,5,2.4))]:
        cam.location=loc;shapes.look_at(cam,(0,0,1.08))
        bpy.context.scene.render.filepath=str(OUT/f'PaladinElite_Base_{title}.png')
        print('BASE_RENDER='+title,flush=True);bpy.ops.render.render(write_still=True)
    print('BASE_COMPLETE',flush=True)


if __name__=='__main__':main()
