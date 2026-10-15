"""Major silhouette pass on the saved direct-edit copy; local Blender only."""
import sys, math, json, hashlib, struct
from pathlib import Path
import bpy, bmesh
import numpy as np
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
import edit_paladin_meshy_copy as direct
import create_paladin_elite as modeler
import elite_textiles as cloth
from elite_ornament import create_materials

OUT=ROOT/'Assets/Characters/Enemies/PaladinElite/DirectMesh/V2'
INPUT=OUT.parent/'Work/Paladin_Meshy_Elite_Edit.blend'
BLEND=OUT/'Paladin_Meshy_Elite_V2.blend'
GLB=OUT/'Paladin_Meshy_Elite_V2.glb'

def reshape(p):
    ax=abs(p.x);side=1 if p.x>=0 else -1;z=p.z
    # Tuck the source's tall collar/shoulder ridge under the fitted additions.
    collar=direct.band(.13,.18,.29,.38,ax)*direct.smooth(1.64,1.75,z)*(1-direct.smooth(1.85,1.90,z))
    p.z-=.12*collar;p.y*=1-.25*collar
    covered=direct.band(.26,.30,.43,.50,ax)*direct.band(1.44,1.52,1.76,1.84,z)
    p.y=.035+(p.y-.035)*(1-.20*covered)
    p.z=1.64+(p.z-1.64)*(1-.20*covered)
    z=p.z
    if z>1.40 and ax>.215:
        w=direct.smooth(.215,.345,ax)*direct.smooth(1.40,1.52,z)
        angle=math.radians(68)*w
        dx=(ax-.25)*(1+.10*w);dz=z-1.65
        p.x=side*(.25+.035*w+dx*math.cos(angle)+dz*math.sin(angle))
        p.z=1.65-dx*math.sin(angle)+dz*math.cos(angle)
        p.y=.035+(p.y-.035)*(1+.16*w)
    else:
        trunk=direct.band(1.08,1.23,1.62,1.75,z)*(1-direct.smooth(.20,.30,ax))
        p.x*=1+.10*trunk
        p.y=.018+(p.y-.018)*(1+.10*trunk)
    head=direct.smooth(1.79,1.87,z)*(1-direct.smooth(.16,.215,ax))
    p.x*=1+.14*head
    p.y=.006+(p.y-.006)*(1+.07*head)
    p.z+=.025*direct.smooth(1.94,2.08,z)*head
    calf=direct.band(.10,.20,.45,.56,z)*direct.smooth(.07,.12,ax)
    cx=side*(.214-.035*max(0,min(1,(z-.12)/.42)))
    p.x=cx+(p.x-cx)*(1+.10*calf)
    p.y=.072+(p.y-.072)*(1+.08*calf)
    return p

def shoulders():
    for sign in (-1,1):
        tag='L' if sign<0 else 'R'
        def dome(u,v):
            a=u*math.tau
            phi=v*1.62
            # A broad forged shell; shallow ridges converge on the crown.
            r=1+.025*math.cos(a*6)*math.sin(phi)**2
            return Vector((sign*(.345+.195*math.sin(phi)*math.cos(a)*r),
                           .030+.181*math.sin(phi)*math.sin(a)*r,
                           1.681+.125*math.cos(phi)-.035*v*max(0,math.cos(a))))
        cap=modeler.surface('V2_Hombrera_'+tag,dome,nu=80,nv=32,trim=False,thickness=.005,flip=sign<0)
        bm=bmesh.new();bm.from_mesh(cap.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(cap.data);bm.free()
        modeler.curve('V2_Hombrera_Borde_'+tag,[[dome(i/160,1) for i in range(161)]],.0032,modeler.M['gold'])
        # Sparse construction ribs; keep the surface subordinate to source armour.
        ribs=[[dome(u,.18+j*.82/45) for j in range(46)] for u in (.07,.19,.31,.43,.57,.69,.81,.93)]
        modeler.curve('V2_Hombrera_Nervios_'+tag,ribs,.00115,modeler.M['gold'])
        # Restrained foliate relief echoes the original mesh's decorated metal.
        def front_panel(u,v):return dome(.585+.325*u,.23+.66*v)+Vector((0,-.0015,.0008))
        modeler.chased('V2_Hombrera_Relieve_'+tag,front_panel,tiles=(2,1),flip=sign<0)
        for i in range(16):
            modeler.rivet('V2_Remache_'+tag,dome(i/16,.95),.0035)
        for j in range(3):
            top=Vector((sign*(.385+j*.021),.032,1.680-j*.065))
            bottom=Vector((sign*(.410+j*.021),.031,1.570-j*.065))
            fn=modeler.sleeve_fn(top,bottom,.108-j*.008,.142-j*.010,depth=1.22,arc=3.80)
            modeler.surface('V2_Lamina_Hombro_'+tag+'_'+str(j+1),fn,nu=44,nv=12,thickness=.004,trim=True,rivets=False)
        modeler.medallion('V2_Broche_Capa_'+tag,(sign*.231,-.170,1.718),.031)

def fit_textiles():
    textiles=cloth.build_textiles(modeler.C['cloth'])
    for im in bpy.data.images:
        if im.name.startswith(('Elite_Tapestry_BaseColor','Elite_Scarf_CocoaWool_BaseColor')):
            pixels=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(pixels)
            rgba=pixels.reshape((-1,4));rgba[:,:3]=np.clip(rgba[:,:3]*4.0,0,1)
            im.pixels.foreach_set(pixels);im.update();im.pack()
    for obj in textiles:
        is_cowl='Cowl' in obj.name
        is_tabard='Tabard' in obj.name
        def fit(p):
            p=Vector(p)
            if is_cowl:
                p.x*=.98;p.y*=.95;p.z-=.044
            elif is_tabard:
                p.y+=.055;p.z=1.225+(p.z-1.23)*.84
            else:
                v=max(0,min(1,(1.729-p.z)/1.43))
                p.x*=1.05;p.y+=.006-.045*(1-v)**4;p.z-=.015
            return p
        if obj.type=='MESH':
            for v in obj.data.vertices:v.co=fit(v.co)
            if is_cowl:
                bm=bmesh.new();bm.from_mesh(obj.data)
                bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
                bm.to_mesh(obj.data);bm.free()
            else:
                for item in obj.data.uv_layers.active.data:
                    item.uv.x*=2;item.uv.y*=1.5
        else:
            for spline in obj.data.splines:
                for p in spline.points:p.co=(*fit(p.co[:3]),1)
    return textiles

def freeze(objects,collection):
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    result=[]
    for obj in objects:
        evaluated=obj.evaluated_get(dg)
        mesh=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=dg)
        if mesh is None:continue
        out=bpy.data.objects.new(obj.name+'_Export',mesh);collection.objects.link(out)
        out.matrix_world=obj.matrix_world.copy();result.append(out)
    return result

def render(camera,title,loc,target=(0,0,1.05),scale=2.45):
    camera.location=loc;camera.data.ortho_scale=scale;direct.look_at(camera,target)
    bpy.context.scene.render.filepath=str(OUT/(title+'.png'))
    bpy.ops.render.render(write_still=True)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source_hash=direct.digest(direct.USER_SOURCE)
    input_hash=direct.digest(INPUT)
    bpy.ops.wm.open_mainfile(filepath=str(INPUT))
    base=bpy.data.objects['Paladin_Meshy_Copia_Editable']
    uv_hash=direct.uv_digest(base.data);top_hash=direct.topology_digest(base.data)
    original_images={direct.image_digest(n.image) for m in base.data.materials for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    key=base.shape_key_add(name='05_Elite_volumen_y_postura',from_mix=True)
    for k in base.data.shape_keys.key_blocks:
        k.value=0
    for v in key.data:v.co=reshape(v.co.copy())
    key.value=1;key.slider_min=0;key.slider_max=1
    base['pose']='Static relaxed pose shaped from original T-pose; no rig'
    base['V2_control']='05 contains previous proportions plus repose. Earlier keys preserved at 0. Do not mix them at full strength.'
    base['V2_original_topology_preserved']=True
    modeler.C={'armor':modeler.collection('02_Elite_Placas_Adicionales'),
               'detail':modeler.collection('03_Elite_Bordes_y_Cierres'),
               'cloth':modeler.collection('04_Elite_Capa_y_Cuello')}
    modeler.M=create_materials()
    steel_image=bpy.data.images['ElitePBR.Steel.Color']
    pixels=np.empty(len(steel_image.pixels),dtype=np.float32);steel_image.pixels.foreach_get(pixels)
    rgba=pixels.reshape((-1,4));rgba[:,:3]*=1.40
    steel_image.pixels.foreach_set(pixels);steel_image.update();steel_image.pack()
    shoulders();fit_textiles()
    assert direct.uv_digest(base.data)==uv_hash and direct.topology_digest(base.data)==top_hash
    camera=bpy.context.scene.camera
    camera.location=(2.7,-5.8,2.6);camera.data.ortho_scale=2.45;direct.look_at(camera,(0,0,1.05))
    scene=bpy.context.scene;scene.render.resolution_x=1200;scene.render.resolution_y=1400
    direct.configure_view(base);bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    render(camera,'TresCuartos',(2.7,-5.8,2.6))
    if '--draft' in sys.argv:
        print('V2_DRAFT_READY',flush=True);return
    objects=[base]+[o for col in modeler.C.values() for o in col.objects]
    frozen_col=modeler.collection('Export_temporal')
    frozen=freeze(objects,frozen_col)
    expected=0
    for obj in frozen:
        obj.data.calc_loop_triangles();expected+=len(obj.data.loop_triangles)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in frozen:obj.select_set(True)
    bpy.context.view_layer.objects.active=frozen[0]
    bpy.ops.export_scene.gltf(filepath=str(GLB),export_format='GLB',use_selection=True,export_apply=True,export_morph=False)
    for obj in frozen:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.collections.remove(frozen_col)
    raw=GLB.read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length])
    external=[entry['uri'] for kind in ('images','buffers') for entry in doc.get(kind,[]) if entry.get('uri') and not entry['uri'].startswith('data:')]
    assert not external
    verify=bpy.data.scenes.new('Validation');bpy.context.window.scene=verify
    bpy.ops.import_scene.gltf(filepath=str(GLB))
    imported=[o for o in verify.objects if o.type=='MESH']
    actual=0
    for obj in imported:
        obj.data.calc_loop_triangles();actual+=len(obj.data.loop_triangles)
        assert all(math.isfinite(c) for v in obj.data.vertices for c in v.co)
        assert len(obj.data.materials)>0
    assert actual==expected,(actual,expected)
    assert not any(o.type in {'ARMATURE','LIGHT','CAMERA'} for o in verify.objects)
    images={n.image for o in imported for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    assert original_images.issubset({direct.image_digest(im) for im in images})
    points=[o.matrix_world@v.co for o in imported for v in o.data.vertices]
    report={'status':'passed','source_sha256':source_hash,'input_blend_sha256':input_hash,
            'original_unchanged':direct.digest(direct.USER_SOURCE)==source_hash==direct.digest(direct.COPY),
            'previous_blend_unchanged':direct.digest(INPUT)==input_hash,'original_uv_preserved':direct.uv_digest(base.data)==uv_hash,
            'original_topology_preserved':direct.topology_digest(base.data)==top_hash,
            'original_pbr_bytes_preserved':True,'original_mesh_triangles':180540,'export_triangles':actual,
            'export_meshes':len(imported),'embedded_images':len(doc.get('images',[])),
            'dimensions_m':[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)],
            'external_references':external,'rig':False,'pose':'Relaxed static pose; original T-pose retained as Basis',
            'changes':['Substantial torso/head/greave proportions','Arms lowered 68 degrees with smooth shoulder transition','Two domed pauldrons and six overlapping lames','Brass borders, rivets and cloak clasps','Long torn cape, gathered cowl and split front cloth']}
    assert report['original_unchanged'] and report['previous_blend_unchanged']
    bpy.context.window.scene=scene
    for obj in list(verify.objects):bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.scenes.remove(verify)
    (OUT/'validation_v2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    render(camera,'Frente',(0,-6,1.20))
    render(camera,'Espalda',(-2.7,5.8,2.6))
    render(camera,'Detalle',(2.2,-5.8,2.3),(0,0,1.67),1.14)
    print('DIRECT_V2_COMPLETE='+json.dumps(report),flush=True)

if __name__=='__main__':main()
