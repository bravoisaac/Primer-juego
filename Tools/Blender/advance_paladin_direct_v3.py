"""Continue the saved V2: real visor openings, fitted gauntlets and waist belt."""
import sys, math, json, struct
from pathlib import Path
import bpy, bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
import edit_paladin_meshy_copy as direct
import advance_paladin_direct_v2 as previous
import create_paladin_elite as build
from elite_ornament import create_materials
OUT=ROOT/'Assets/Characters/Enemies/PaladinElite/DirectMesh/V3'
INPUT=OUT.parent/'V2/Paladin_Meshy_Elite_V2.blend'
BLEND=OUT/'Paladin_Meshy_Elite_V3.blend'
GLB=OUT/'Paladin_Meshy_Elite_V3.glb'

def log(message):print(message,flush=True)

def evaluated_mesh(obj):
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    return bpy.data.meshes.new_from_object(obj.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)

def make_bvh(obj):
    mesh=evaluated_mesh(obj)
    tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[p.vertices[:] for p in mesh.polygons])
    bpy.data.meshes.remove(mesh)
    return tree

def front(tree,x,z,offset=.003):
    hit=tree.ray_cast(Vector((x,-.65,z)),Vector((0,1,0)),1.1)[0]
    return Vector((x,hit.y-offset,z)) if hit else None

def back_of_hand(tree,sign,y,z):
    hit=tree.ray_cast(Vector((sign*.75,y,z)),Vector((-sign,0,0)),.40)[0]
    return hit if hit and abs(hit.x)>.35 else None

def refine_original(base):
    key=base.shape_key_add(name='06_V3_Cuello_y_ajustes',from_mix=True)
    for k in base.data.shape_keys.key_blocks:k.value=0
    for item in key.data:
        p=item.co;ax=abs(p.x)
        # Fold down the old rear collar crests under the cowl and cape.
        mask=direct.band(.10,.15,.27,.33,ax)*direct.smooth(.04,.11,p.y)*direct.band(1.60,1.66,1.79,1.85,p.z)
        p.z-=.14*mask;p.y-=.065*mask
        center=direct.band(1.57,1.62,1.70,1.73,p.z)*(1-direct.smooth(.10,.15,ax))*direct.smooth(.08,.14,p.y)
        p.y-=.075*center;p.z-=.020*center
    key.value=1;key.slider_min=0;key.slider_max=1
    base['V3_control']='06 includes V2 plus collar correction. 01-05 at zero. Helmet openings are a separate Boolean modifier.'

def helmet(base,tree):
    cutters=build.C['cutters'];parts=[]
    for sign in (-1,1):
        bpy.ops.mesh.primitive_cube_add(size=1,location=(sign*.055,-.12,1.963))
        ob=bpy.context.object;ob.name='EyeSlot_Cutter';ob.scale=(.080,.32,.012)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);parts.append(ob)
        for z,xs in [(1.907,(.038,.055,.072)),(1.890,(.040,.057,.074))]:
            for x in xs:
                bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.0036,depth=.32,
                    location=(sign*x,-.12,z),rotation=(math.pi/2,0,0))
                parts.append(bpy.context.object)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:ob.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
    cutter=bpy.context.object;cutter.name='V3_Cortadores_Ojos_y_Respiraderos'
    for col in list(cutter.users_collection):col.objects.unlink(cutter)
    cutters.objects.link(cutter)
    # Cut walls use dark steel rather than arbitrary original atlas pixels.
    base.data.materials.append(build.M['black'])
    cutter.data.materials.clear()
    for mat in base.data.materials:cutter.data.materials.append(mat)
    for face in cutter.data.polygons:face.material_index=len(base.data.materials)-1
    modifier=base.modifiers.new('V3_Aberturas_reales_del_visor','BOOLEAN')
    modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
    normals=base.modifiers.new('V3_Normales_tras_cortes','WEIGHTED_NORMAL')
    normals.keep_sharp=True;normals.weight=30
    cutter.hide_render=True;cutter.hide_set(True);cutter.display_type='WIRE'
    cutter['purpose']='Editable cutting tool, excluded from exported model'
    for sign in (-1,1):
        # Recessed dark fabric behind the openings, not painted-on eye lines.
        def lining(u,v,sign=sign):
            x=sign*(.012+.088*u);z=1.877+.101*v
            p=front(tree,x,z,-.025)
            return p if p else Vector((x,-.01,z))
        build.surface('V3_Interior_Visor_'+str(sign),lining,mat=build.M['black'],nu=24,nv=18,thickness=.001,trim=False,flip=sign<0)
        brow=[front(tree,sign*(.012+.086*i/48),1.976,.004) for i in range(49)]
        build.curve('V3_Ceja_Visor_'+str(sign),[[p for p in brow if p is not None]],.0025,build.M['gold'])
        low=[front(tree,sign*(.013+.080*i/48),1.953,.003) for i in range(49)]
        build.curve('V3_Labio_Visor_'+str(sign),[[p for p in low if p is not None]],.0014,build.M['gold'])
        pivot=front(tree,sign*.102,1.932,.005)
        if pivot is not None:
            build.sphere('V3_Pivote_Visor',pivot,(.008,.004,.008),build.M['gold'],segments=20)
    # Tapered central ridge links the brow to the pointed original helmet.
    path=[front(tree,0,1.977+i*.104/65,.003) for i in range(66)]
    build.curve('V3_Nervio_Central_Casco',[[p for p in path if p is not None]],.0018,build.M['gold'])
    profile=[]
    for i in range(101):
        p=front(tree,0,1.830+.251*i/100,.006)
        profile.append(p.y if p is not None else -.05)
    # Broad enough to bridge the irregular source crest, with a clean ridge.
    for _ in range(2):profile=[profile[0]]+[(profile[i-1]+2*profile[i]+profile[i+1])/4 for i in range(1,100)]+[profile[-1]]
    def crest(u,v):
        index=min(99,int(v*100));t=v*100-index
        y=profile[index]*(1-t)+profile[index+1]*t
        return Vector(((u-.5)*(.009+.003*math.sin(math.pi*v)),y+.0035*abs(2*u-1),1.830+.251*v))
    build.surface('V3_Refuerzo_Cresta_Casco',crest,mat=build.M['gold'],nu=6,nv=100,thickness=.0015,trim=False)
    log('V3 helmet with non-destructive Boolean prepared')

def gauntlets(tree):
    made=0
    for sign in (-1,1):
        tag='L' if sign<0 else 'R'
        top=Vector((sign*.407,-.035,1.268));bottom=Vector((sign*.427,-.052,1.176))
        cuff=build.sleeve_fn(top,bottom,.058,.049,depth=1.40,arc=5.5)
        build.surface('V3_Puno_Acampanado_'+tag,cuff,nu=48,nv=18,thickness=.0035,trim=True)
        def dorsal(u,v,sign=sign):
            y=-.061+(u-.5)*(.079+.014*math.sin(math.pi*v))
            z=1.090+.098*v-.009*math.sin(math.pi*u)*(1-v)
            hit=back_of_hand(tree,sign,y,z)
            x=abs(hit.x) if hit else .437
            return Vector((sign*(x+.011+.003*math.sin(math.pi*u)*math.sin(math.pi*v)),y,z))
        build.surface('V3_Placa_Dorso_'+tag,dorsal,nu=30,nv=28,thickness=.0025,trim=True,flip=sign<0)
        ridges=[[dorsal(u,j/30)+Vector((sign*.001,0,0)) for j in range(4,29)] for u in (.23,.50,.77)]
        build.curve('V3_Nervios_Guantelete_'+tag,ridges,.0013,build.M['gold'])
        for digit,y in enumerate((-.098,-.076,-.054,-.032)):
            for joint,z in enumerate((1.080,1.057,1.035)):
                center=back_of_hand(tree,sign,y,z)
                if center is None:continue
                def finger(u,v,sign=sign,y=y,z=z,center=center):
                    yy=y+(u-.5)*.017;zz=z+(v-.5)*.019
                    hit=back_of_hand(tree,sign,yy,zz)
                    x=abs(hit.x) if hit is not None else abs(center.x)
                    return Vector((sign*(x+.003+.003*math.sin(math.pi*u)),yy,zz))
                build.surface('V3_Falange_'+tag+'_'+str(digit)+'_'+str(joint),finger,nu=10,nv=8,thickness=.0016,trim=False,flip=sign<0)
                build.curve('V3_Borde_Falange_'+tag,[[finger(i/16,0) for i in range(17)]],.001,build.M['gold'])
                made+=1
        for u in (.13,.87):
            p=dorsal(u,.82)
            build.sphere('V3_Remache_Guantelete',p,(.003,.004,.004),build.M['gold'],segments=12)
    log('V3 fitted finger plates: '+str(made))
    return made

def belt(tree):
    def strap(u,v):
        a=(u-.5)*math.tau;z=1.221+.040*v
        d=Vector((math.sin(a),-math.cos(a),0))
        hit=tree.ray_cast(d*.32+Vector((0,0,z)),-d,.32)[0]
        if hit is None:hit=d*.205+Vector((0,0,z))
        return hit+d*.013
    build.surface('V3_Cinturon_Cuero',strap,mat=build.M['leather'],nu=160,nv=16,thickness=.003,trim=False)
    lines=[[strap(i/180,v) for i in range(181)] for v in (.10,.90)]
    build.curve('V3_Costuras_Cinturon',lines,.0009,build.M['gold'])
    center=strap(.5,.5)+Vector((.018,-.009,0))
    outline=[(-.030,-.022),(.030,-.022),(.035,-.017),(.035,.017),(.030,.022),(-.030,.022),(-.035,.017),(-.035,-.017),(-.030,-.022)]
    build.curve('V3_Hebilla_Forjada',[[center+Vector((x,0,z)) for x,z in outline]],.004,build.M['gold'])
    build.curve('V3_Aguja_Hebilla',[[center+Vector((-.020,-.003,0)),center+Vector((.033,-.003,0))]],.0023,build.M['gold'])

def material_finish():
    # Only derived local materials; the source images stay byte-identical.
    for name in ('ElitePBR.Steel.Color','ElitePBR.Steel.Roughness'):
        im=bpy.data.images.get(name)
        if not im:continue
        width,height=im.size
        pixels=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(pixels)
        rgba=pixels.reshape((height,width,4));yy,xx=np.mgrid[:height,:width]
        rng=np.random.default_rng(31014)
        wear=np.zeros((height,width),dtype=np.float32)
        for grid,weight in ((7,.55),(31,.30),(107,.15)):
            lattice=rng.random((grid,grid))*2-1
            gx=xx/width*grid;gy=yy/height*grid
            ix=np.floor(gx).astype(int);iy=np.floor(gy).astype(int)
            fx=gx-ix;fy=gy-iy;fx=fx*fx*(3-2*fx);fy=fy*fy*(3-2*fy)
            wear+=weight*(lattice[iy%grid,ix%grid]*(1-fx)*(1-fy)
                +lattice[iy%grid,(ix+1)%grid]*fx*(1-fy)
                +lattice[(iy+1)%grid,ix%grid]*(1-fx)*fy
                +lattice[(iy+1)%grid,(ix+1)%grid]*fx*fy)
        grain=rng.normal(0,.018,(height,width))
        if name.endswith('Color'):
            rgba[:,:,:3]*=(.83+.10*wear+grain)[:,:,None]
        else:rgba[:,:,:3]=np.clip(rgba[:,:,:3]+(.075+.04*wear)[:,:,None],.25,.85)
        im.pixels.foreach_set(pixels);im.update();im.pack()
    for mat in bpy.data.materials:
        if 'tapestry' in mat.name or 'scarf matte' in mat.name:
            shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
            shader.inputs['Sheen Weight'].default_value=.04
    for im in bpy.data.images:
        if im.name.startswith('Elite_Tapestry_BaseColor'):
            pixels=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(pixels)
            rgba=pixels.reshape((-1,4));rgba[:,:3]*=.82
            im.pixels.foreach_set(pixels);im.update();im.pack()

def export_validate(objects,base,source_images,input_hash,uv_hash,top_hash):
    col=build.collection('TemporaryExport');frozen=previous.freeze(objects,col)
    expected=0
    for ob in frozen:ob.data.calc_loop_triangles();expected+=len(ob.data.loop_triangles)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in frozen:ob.select_set(True)
    bpy.context.view_layer.objects.active=frozen[0]
    bpy.ops.export_scene.gltf(filepath=str(GLB),export_format='GLB',use_selection=True,export_apply=True,export_morph=False)
    for ob in frozen:bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.collections.remove(col)
    raw=GLB.read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length])
    external=[item['uri'] for kind in ('images','buffers') for item in doc.get(kind,[]) if item.get('uri') and not item['uri'].startswith('data:')]
    assert not external
    original_scene=bpy.context.scene;verify=bpy.data.scenes.new('ValidateV3');bpy.context.window.scene=verify
    bpy.ops.import_scene.gltf(filepath=str(GLB))
    meshes=[ob for ob in verify.objects if ob.type=='MESH'];actual=0;points=[]
    for ob in meshes:
        ob.data.calc_loop_triangles();actual+=len(ob.data.loop_triangles)
        assert ob.data.materials and all(math.isfinite(c) for v in ob.data.vertices for c in v.co)
        points.extend(ob.matrix_world@v.co for v in ob.data.vertices)
    assert actual==expected
    assert not any(ob.type in {'CAMERA','LIGHT','ARMATURE'} or 'Cortador' in ob.name for ob in verify.objects)
    images={n.image for ob in meshes for mat in ob.data.materials for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    assert source_images.issubset({direct.image_digest(im) for im in images})
    dimensions=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
    assert max(dimensions)<2.2
    result={'status':'passed','triangles':actual,'meshes':len(meshes),'embedded_images':len(doc.get('images',[])),
            'external_references':external,'dimensions_m':dimensions,'source_pbr_bytes_preserved':True,
            'source_base_uv_preserved':direct.uv_digest(base.data)==uv_hash,'source_base_topology_preserved':direct.topology_digest(base.data)==top_hash,
            'v2_file_unchanged':direct.digest(INPUT)==input_hash,'original_glb_unchanged':direct.digest(direct.USER_SOURCE)==direct.digest(direct.COPY),
            'helmet_openings':'Evaluated Boolean on original mesh; editable cutter excluded from export','rig':False}
    assert all(result[k] for k in ('source_base_uv_preserved','source_base_topology_preserved','v2_file_unchanged','original_glb_unchanged'))
    bpy.context.window.scene=original_scene
    for ob in list(verify.objects):bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.scenes.remove(verify)
    return result

def main():
    OUT.mkdir(parents=True,exist_ok=True);input_hash=direct.digest(INPUT)
    bpy.ops.wm.open_mainfile(filepath=str(INPUT));base=bpy.data.objects['Paladin_Meshy_Copia_Editable']
    uv_hash=direct.uv_digest(base.data);top_hash=direct.topology_digest(base.data)
    source_images={direct.image_digest(n.image) for mat in base.data.materials for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    build.C={'armor':build.collection('05_V3_Protecciones'), 'detail':build.collection('06_V3_Cierres_y_Bordes'), 'cutters':build.collection('91_V3_Herramientas_Visor')}
    build.M=create_materials();refine_original(base);tree=make_bvh(base)
    gauntlet_plates=gauntlets(tree);belt(tree);helmet(base,tree);material_finish()
    # Check the evaluated opening itself, before fitting the dark interior.
    cut_tree=make_bvh(base);hits=[]
    for sign in (-1,1):
        hit=cut_tree.ray_cast(Vector((sign*.052,-.65,1.963)),Vector((0,1,0)),1.1)[0]
        hits.append(None if hit is None else hit.y)
        assert hit is None or hit.y>-.01,'Eye opening did not cut the original shell'
    log('V3 eye aperture checks: '+str(hits))
    camera=bpy.context.scene.camera;camera.location=(2.7,-5.8,2.6);camera.data.ortho_scale=2.45
    direct.look_at(camera,(0,0,1.05));direct.configure_view(base)
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    previous.OUT=OUT
    previous.render(camera,'TresCuartos',(2.7,-5.8,2.6))
    previous.render(camera,'Casco',(2.0,-6,2.3),(0,-.04,1.95),.53)
    if '--draft' in sys.argv:log('V3_DRAFT_READY');return
    objects=[ob for col in bpy.context.scene.collection.children if col.name not in ('90_Estudio','91_V3_Herramientas_Visor') for ob in col.objects if ob.type in {'MESH','CURVE'}]
    report=export_validate(objects,base,source_images,input_hash,uv_hash,top_hash)
    report.update({'finger_plates':gauntlet_plates,'eye_opening_ray_y':hits,'input_sha256':input_hash})
    (OUT/'validation_v3.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    previous.render(camera,'Frente',(0,-6,1.20))
    previous.render(camera,'Espalda',(-2.7,5.8,2.6))
    previous.render(camera,'Guantelete',(4,-4,1.8),(.42,-.05,1.15),.40)
    log('DIRECT_V3_COMPLETE='+json.dumps(report))

if __name__=='__main__':main()
