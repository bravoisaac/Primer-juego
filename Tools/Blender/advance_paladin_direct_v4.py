"""Reference-led siege silhouette: waist armour, knee cops, greaves and sabatons."""
import sys, math, json
from pathlib import Path
import bpy, bmesh
from mathutils import Vector
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
import edit_paladin_meshy_copy as direct
import advance_paladin_direct_v2 as v2
import advance_paladin_direct_v3 as v3
import create_paladin_elite as build
from elite_ornament import create_materials
OUT=ROOT/'Assets/Characters/Enemies/PaladinElite/DirectMesh/V4'
INPUT=OUT.parent/'V3/Paladin_Meshy_Elite_V3.blend'
BLEND=OUT/'Paladin_Meshy_Elite_V4.blend'
GLB=OUT/'Paladin_Meshy_Elite_V4.glb'

def body_shape(p):
    p=Vector(p);ax=abs(p.x);z=p.z
    trunk=direct.band(1.06,1.20,1.58,1.73,z)*(1-direct.smooth(.24,.36,ax))
    p.x*=1+.085*trunk;p.y*=1+.045*trunk
    waist=direct.band(1.03,1.12,1.27,1.34,z)*(1-direct.smooth(.23,.35,ax))
    p.x*=1+.045*waist
    return p

def warp_object(obj,fn):
    world=obj.matrix_world.copy();inverse=world.inverted()
    if obj.type=='MESH':
        for vertex in obj.data.vertices:vertex.co=inverse@fn(world@vertex.co)
    elif obj.type=='CURVE':
        for spline in obj.data.splines:
            for point in spline.points:
                point.co=(*(inverse@fn(world@Vector(point.co[:3]))),1)

def reference_proportions(base):
    key=base.shape_key_add(name='07_V4_Proporciones_Asedio',from_mix=True)
    for k in base.data.shape_keys.key_blocks:k.value=0
    for p in key.data:p.co=body_shape(p.co)
    key.value=1;key.slider_min=0;key.slider_max=1
    for col in bpy.context.scene.collection.children:
        if col.name.startswith(('90_','91_')):continue
        for ob in col.objects:
            if ob!=base:warp_object(ob,body_shape)
    base['V4_control']='07 includes the saved V3 and broader torso/waist. Earlier keys remain at zero.'

def textiles():
    for ob in bpy.data.objects:
        if ob.name.startswith('Elite_Cape'):
            def cape(p):
                p=Vector(p);v=max(0,min(1,(1.714-p.z)/1.43))
                p.z+=.145*v*v;p.x*=1-.10*v
                return p
            warp_object(ob,cape)
        elif ob.name.startswith('Elite_Tabard'):
            def tabard(p):
                p=Vector(p);v=max(0,min(1,(1.225-p.z)/.80));sign=1 if p.x>=0 else -1
                p.z+=.135*v**1.3
                p.x+=sign*.009*math.sin(v*6+sign)*v
                p.y-=.012*math.sin(v*5+sign)*math.sin(v*math.pi)
                return p
            warp_object(ob,tabard)
        elif ob.name.startswith('Elite_Cowl'):
            def cowl(p):
                p=Vector(p);front=direct.smooth(.01,.14,-p.y)
                p.z-=.055*front*direct.smooth(1.64,1.80,p.z)
                return p
            warp_object(ob,cowl)
    for image in bpy.data.images:
        if image.name.startswith(('Elite_Tapestry_BaseColor','Elite_Scarf_CocoaWool_BaseColor')):
            data=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(data)
            rgba=data.reshape((-1,4));rgba[:,:3]*=np.array((.80,.87,.97))
            image.pixels.foreach_set(data);image.update();image.pack()

def rivet_pair(name,fn):
    for u in (.08,.92):
        for v in (.12,.88):build.rivet(name,fn(u,v),.0035)

def lower_armour():
    for sign in (-1,1):
        tag='L' if sign<0 else 'R'
        def tasset(u,v,sign=sign):
            q=2*u-1;w=.106-.018*v
            return Vector((sign*(.198+.033*(1-v))+q*w,
                -.225-.018*math.sin(math.pi*v)+.042*q*q,
                .805+.375*v+.025*q*q*(1-v)))
        build.surface('V4_Faldon_Metalico_'+tag,tasset,nu=48,nv=48,thickness=.005,trim=True)
        rivet_pair('V4_Remaches_Faldon_'+tag,tasset)
        def inset(u,v):return tasset(.08+.84*u,.08+.72*v)+Vector((0,-.0015,0))
        build.chased('V4_Grabado_Faldon_'+tag,inset,tiles=(1,2))
        for j in range(2):
            def suspension(u,v,j=j):return tasset(u,.82+j*.075+v*.075)+Vector((0,-.006,0))
            build.surface('V4_Lamina_Cintura_'+tag+str(j),suspension,nu=36,nv=6,thickness=.003,trim=True)
            for u in (.12,.88):build.rivet('V4_Remanente_Cintura',suspension(u,.5),.004)
        for j in range(2):
            top=(sign*.190,.020,.865-j*.073);bottom=(sign*.194,.020,.758-j*.073)
            fn=build.sleeve_fn(top,bottom,.118,.116,depth=1.38,arc=3.25)
            build.surface('V4_Lamina_Muslo_'+tag+str(j),fn,nu=40,nv=12,thickness=.004,trim=True)
        def knee(u,v,sign=sign):
            q=2*u-1;w=.034+.077*math.sin(math.pi*v)**.7
            return Vector((sign*.190+q*w,-.148-.057*(1-abs(q))*(math.sin(math.pi*v)**.65),.535+.220*v))
        build.surface('V4_Rodillera_Angular_'+tag,knee,nu=40,nv=36,thickness=.005,trim=True)
        border=[knee(u,v)+Vector((0,-.002,0)) for u,v in ((.5,.18),(.22,.50),(.5,.82),(.78,.50),(.5,.18))]
        cross=[[knee(.5,.24+i*.52/30)+Vector((0,-.003,0)) for i in range(31)],
               [knee(.28+i*.44/30,.52)+Vector((0,-.003,0)) for i in range(31)]]
        build.curve('V4_Emblema_Rodilla_'+tag,[border]+cross,.0022,build.M['gold'])
        for side in (-1,1):
            build.sphere('V4_Pivote_Rodilla',(sign*.190+side*.105,-.145,.645),(.011,.006,.014),build.M['gold'],segments=20)
        def greave(u,v,sign=sign):
            a=(u-.5)*5.65
            r=.073+.029*v+.014*math.sin(math.pi*v)
            return Vector((sign*(.218-.026*v)+r*math.sin(a),
                .042-(.112+.036*v)*math.cos(a)-.010*math.exp(-a*a*18),
                .125+.423*v+.018*math.cos(a)*(1-v)))
        build.surface('V4_Greba_Envolvente_'+tag,greave,nu=64,nv=56,thickness=.004,trim=True)
        build.curve('V4_Nervio_Greba_'+tag,[[greave(.5,j/80)+Vector((0,-.001,0)) for j in range(81)]],.0023,build.M['gold'])
        def shin_inlay(u,v):return greave(.32+.36*u,.12+.77*v)+Vector((0,-.001,0))
        build.chased('V4_Grabado_Greba_'+tag,shin_inlay,tiles=(1,2))
        rivet_pair('V4_Remaches_Greba_'+tag,greave)
        for j in range(2):
            fn=build.sleeve_fn((sign*.217,.025,.202-j*.043),(sign*.223,.025,.139-j*.043),.079,.084,depth=1.45,arc=3.7)
            build.surface('V4_Lamina_Tobillo_'+tag+str(j),fn,nu=40,nv=10,thickness=.003,trim=True)

def boots():
    for sign in (-1,1):
        tag='L' if sign<0 else 'R'
        def shoe(u,t,sign=sign):
            a=(u-.5)*math.pi
            width=.070+.014*math.sin(math.pi*t)
            cx=sign*(.217+.025*(1-t))
            h=.058+.065*direct.smooth(.15,.72,t)+.030*math.exp(-((t-.72)/.19)**2)
            return Vector((cx+width*math.sin(a),-.260+.390*t,.024+h*math.cos(a)))
        build.surface('V4_Bota_Base_'+tag,shoe,mat=build.M['leather'],nu=40,nv=48,thickness=.003,trim=False)
        for j in range(6):
            def plate(u,v,j=j):return shoe(u,.005+j*.115+v*.145)+Vector((0,0,.004+j*.0003))
            build.surface('V4_Escarpe_Placa_'+tag+str(j),plate,nu=36,nv=10,thickness=.003,trim=False)
            build.curve('V4_Escarpe_Borde_'+tag+str(j),[[plate(i/48,0) for i in range(49)]],.002,build.M['gold'])
        def toe(u,v,sign=sign):
            q=2*u-1;z=.024+.062*math.sqrt(max(0,1-q*q))*v
            return Vector((sign*.242+.070*q,-.263+.003*v,z))
        build.surface('V4_Puntera_Cerrada_'+tag,toe,nu=40,nv=14,thickness=.003,trim=False)
        build.curve('V4_Puntera_Borde_'+tag,[[toe(i/48,1) for i in range(49)]],.002,build.M['gold'])
        # Extruded, rounded leather sole; underside remains at floor level.
        outline=[]
        for i in range(49):
            a=i*math.tau/48
            y=-.065+.205*math.cos(a);t=(y+.270)/.41
            outline.append((sign*(.217+.025*(1-t))+.077*math.sin(a),y))
        verts=[(x,y,z) for z in (.001,.025) for x,y in outline[:-1]];n=48
        faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]
        faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
        uv=[((x-sign*.22)/.2+.5,(y+.27)/.41) for x,y,z in verts]
        sole=build.mesh('V4_Suela_'+tag,verts,faces,build.M['leather'],uv=uv)
        bevel=sole.modifiers.new('Rounded sole edge','BEVEL');bevel.width=.003;bevel.segments=2
        for j in range(9):
            y=-.225+j*.039
            for side in (-1,1):
                build.sphere('V4_Clavo_Suela',(sign*.23+side*.068,y,.015),(.0025,.003,.003),build.M['gold'],segments=8)

def soften_source_normal(base):
    old=base.data.materials[0];old.use_fake_user=True
    mat=old.copy();mat.name='V4_Meshy_PBR_Grabado_Atenuado';base.data.materials[0]=mat
    for node in mat.node_tree.nodes:
        if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.45
    mat['change']='Normal intensity 0.45; original images preserved byte-for-byte'

def main():
    OUT.mkdir(parents=True,exist_ok=True);input_hash=direct.digest(INPUT)
    bpy.ops.wm.open_mainfile(filepath=str(INPUT));base=bpy.data.objects['Paladin_Meshy_Copia_Editable']
    uv=direct.uv_digest(base.data);top=direct.topology_digest(base.data)
    images={direct.image_digest(n.image) for mat in base.data.materials for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    reference_proportions(base);textiles();soften_source_normal(base)
    build.C={'armor':build.collection('07_V4_Armadura_Inferior'),'detail':build.collection('08_V4_Grabados_y_Herrajes')}
    build.M=create_materials();lower_armour();boots()
    camera=bpy.context.scene.camera;camera.location=(2.7,-5.8,2.6);camera.data.ortho_scale=2.45;direct.look_at(camera,(0,0,1.05))
    direct.configure_view(base);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    v2.OUT=OUT;v2.render(camera,'TresCuartos',(2.7,-5.8,2.6))
    v2.render(camera,'Espalda',(-2.7,5.8,2.6))
    if '--draft' in sys.argv:print('V4_DRAFT_READY',flush=True);return
    objects=[ob for col in bpy.context.scene.collection.children if not col.name.startswith(('90_','91_')) for ob in col.objects if ob.type in {'MESH','CURVE'}]
    v3.GLB=GLB;v3.INPUT=INPUT
    report=v3.export_validate(objects,base,images,input_hash,uv,top)
    report['v3_file_unchanged']=report.pop('v2_file_unchanged')
    report['input_sha256']=input_hash
    report['changes']=['Broader torso and waist','Shorter cape, irregular front cloth and lower cowl','Two tassets and four thigh lames','Angular knee cops and wrapped greaves','Articulated broad sabatons with soles','Original normal-map intensity reduced, original image bytes preserved']
    (OUT/'validation_v4.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    v2.render(camera,'Frente',(0,-6,1.20))
    v2.render(camera,'Piernas',(2.6,-5.8,1.5),(0,-.03,.61),1.31)
    print('DIRECT_V4_COMPLETE='+json.dumps(report),flush=True)

if __name__=='__main__':main()
