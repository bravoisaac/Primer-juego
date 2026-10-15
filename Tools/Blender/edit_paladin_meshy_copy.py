"""First direct edit of the user's copied Meshy mesh, preserving its topology.

Original GLB is copied byte-for-byte. Blender edits are independent shape keys;
the exported GLB is a frozen view of the edited original mesh, with its PBR maps.
"""
import hashlib
import json
import math
import struct
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Assets/Characters/Enemies/PaladinElite/DirectMesh'
USER_SOURCE=Path(r'C:\Users\isaac\Downloads\Meshy_AI_Gilded_Sentinel_1012232218_texture.glb')
COPY=OUT/'Source/Paladin_Meshy_Original_Copy.glb'
BLEND=OUT/'Work/Paladin_Meshy_Elite_Edit.blend'
EXPORT=OUT/'Exports/Paladin_Meshy_Elite_Edit.glb'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def smooth(a,b,x):
    t=max(0,min(1,(x-a)/(b-a)))
    return t*t*(3-2*t)


def band(a,b,c,d,x):return smooth(a,b,x)*(1-smooth(c,d,x))


def gaussian(x,center,width):return math.exp(-((x-center)/width)**2)


def uv_digest(mesh):
    h=hashlib.sha256()
    for layer in mesh.uv_layers:
        for item in layer.data:h.update(struct.pack('<2f',*item.uv))
    return h.hexdigest()


def topology_digest(mesh):
    h=hashlib.sha256()
    for polygon in mesh.polygons:
        h.update(struct.pack('<I',len(polygon.vertices)))
        for index in polygon.vertices:h.update(struct.pack('<I',index))
    return h.hexdigest()


def image_digest(image):
    if image.packed_file:return hashlib.sha256(bytes(image.packed_file.data)).hexdigest()
    raise AssertionError('A source PBR image is not embedded: '+image.name)


def look_at(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()


def setup_studio():
    scene=bpy.context.scene
    studio=bpy.data.collections.new('90_Estudio');scene.collection.children.link(studio)
    def move(obj):
        for col in list(obj.users_collection):col.objects.unlink(obj)
        studio.objects.link(obj)
        return obj
    scene.world=bpy.data.worlds.new('DirectEdit_Studio');scene.world.use_nodes=True
    bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
    bg.inputs['Color'].default_value=(.04,.05,.065,1);bg.inputs['Strength'].default_value=.35
    for name,loc,power,size,color in [
        ('Key',(-3,-4,4.5),650,3.4,(1,.89,.76)),
        ('Fill',(3,-2,2.8),450,3.0,(.76,.85,1)),
        ('Rim',(1,3,3.2),800,2.4,(1,.90,.78)),
    ]:
        bpy.ops.object.light_add(type='AREA',location=loc)
        obj=move(bpy.context.object);obj.name=name;obj.data.energy=power;obj.data.size=size
        obj.data.color=color;look_at(obj,(0,0,1.1))
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.005))
    obj=move(bpy.context.object);obj.name='StudioFloor'
    mat=bpy.data.materials.new('StudioFloor');mat.use_nodes=True
    node=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    node.inputs['Base Color'].default_value=(.055,.065,.079,1);node.inputs['Roughness'].default_value=.86
    obj.data.materials.append(mat)
    bpy.ops.object.camera_add(location=(2.7,-5.8,2.6))
    camera=move(bpy.context.object);camera.name='Camera_DirectEdit'
    camera.data.type='ORTHO';camera.data.ortho_scale=2.52
    look_at(camera,(0,0,1.045));scene.camera=camera
    scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x=1100;scene.render.resolution_y=1300;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    scene.render.film_transparent=False
    return camera


def edits(model,basis):
    keys=[]
    def add(name,fn,description):
        key=model.shape_key_add(name=name,from_mix=False)
        for vertex,origin in zip(key.data,basis):vertex.co=fn(origin.copy())
        key.value=1;key.slider_min=0;key.slider_max=1.5
        keys.append(key);model['edit_'+name]=description
    def torso(p):
        z=p.z;ax=abs(p.x)
        trunk=band(1.08,1.25,1.60,1.76,z)*(1-smooth(.205,.32,ax))
        # Broad, smooth proportional edits retain all plate borders and UVs.
        p.x*=1+.080*trunk
        p.y=(p.y-.018)*(1+.075*trunk)+.018
        waist=gaussian(z,1.20,.105)*(1-smooth(.19,.28,ax))
        p.x*=1-.025*waist
        return p
    def shoulders(p):
        ax=abs(p.x);side=1 if p.x>=0 else -1
        shoulder=gaussian(ax,.295,.105)*gaussian(p.z,1.69,.115)
        p.x+=side*.012*shoulder
        p.y=.039+(p.y-.039)*(1+.075*shoulder)
        p.z+=.008*shoulder
        # Thicken the arm cross section around its existing T-pose axis.
        forearm=band(.43,.50,.62,.68,ax)*gaussian(p.z,1.605,.10)
        p.y=.027+(p.y-.027)*(1+.065*forearm)
        p.z=1.605+(p.z-1.605)*(1+.055*forearm)
        return p
    def legs(p):
        side=1 if p.x>=0 else -1
        calf=band(.10,.20,.43,.54,p.z)*smooth(.08,.12,abs(p.x))
        # Anatomical center follows the slanted greave, keeping the feet fixed.
        cx=side*(.214-.035*max(0,min(1,(p.z-.12)/.42)))
        p.x=cx+(p.x-cx)*(1+.12*calf)
        p.y=.072+(p.y-.072)*(1+.09*calf)
        return p
    def helmet(p):
        head=smooth(1.78,1.87,p.z)*(1-smooth(.135,.20,abs(p.x)))
        p.x*=1+.045*head
        p.y=.006+(p.y-.006)*(1+.025*head)
        return p
    add('01_Peto_y_cintura',torso,'Peto +8% local width / +7.5% depth, restrained waist')
    add('02_Hombros_y_brazales',shoulders,'Shoulder placement +12mm per side; fuller original arm plates')
    add('03_Volumen_grebas',legs,'Greave cross section +12% width / +9% depth; fixed feet')
    add('04_Ancho_casco',helmet,'Helmet width +4.5% with gradual neck transition')
    return keys


def configure_view(model):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active=model
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                space=area.spaces.active;space.shading.type='MATERIAL'
                space.shading.use_scene_world=False;space.shading.use_scene_lights=False
                space.overlay.show_overlays=False
                space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_zoom=0


def validate_export(model,frozen,source_images):
    raw=EXPORT.read_bytes();chunk_length,chunk_type=struct.unpack_from('<I4s',raw,12)
    assert raw[:4]==b'glTF' and chunk_type==b'JSON'
    document=json.loads(raw[20:20+chunk_length].decode('utf-8'))
    external=[item['uri'] for key in ('buffers','images') for item in document.get(key,[])
              if item.get('uri') and not item['uri'].startswith('data:')]
    assert not external,'Edited GLB has external file dependencies'
    original_scene=bpy.context.scene
    scene=bpy.data.scenes.new('VerifyActualGLB');bpy.context.window.scene=scene
    bpy.ops.import_scene.gltf(filepath=str(EXPORT))
    meshes=[o for o in scene.objects if o.type=='MESH']
    assert len(meshes)==1,'Edited GLB must contain the original mesh only'
    imported=meshes[0];imported.data.calc_loop_triangles();frozen.data.calc_loop_triangles()
    assert len(imported.data.loop_triangles)==len(model.data.polygons)==180540
    assert imported.data.uv_layers and len(imported.data.materials)==1
    assert not any(o.type in {'CAMERA','LIGHT','ARMATURE'} for o in scene.objects)
    assert all(math.isfinite(c) for v in imported.data.vertices for c in v.co)
    images={n.image for m in imported.data.materials for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    assert len(images)==3,'PBR maps missing'
    assert {image_digest(im) for im in images}==set(source_images.values()),'PBR image bytes changed'
    # glTF can duplicate vertices at UV seams, so compare evaluated triangle
    # surfaces and image payloads rather than requiring its vertex indexing.
    imported_coords=sorted(tuple(round(c,5) for c in (imported.matrix_world@v.co)) for v in imported.data.vertices)
    frozen_coords=sorted(tuple(round(c,5) for c in (frozen.matrix_world@v.co)) for v in frozen.data.vertices)
    assert imported_coords==frozen_coords,'Geometry changed during the GLB round trip'
    report={'status':'passed','meshes':len(meshes),'triangles':len(imported.data.loop_triangles),
            'images':len(images),'image_bytes_unchanged':True,'round_trip_geometry_matches':True,
            'external_references':external}
    bpy.context.window.scene=original_scene
    for obj in list(scene.objects):bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.scenes.remove(scene)
    return report


def main():
    for folder in ('Source','Work','Exports','Preview'):(OUT/folder).mkdir(parents=True,exist_ok=True)
    original_hash=digest(USER_SOURCE)
    if not COPY.exists():COPY.write_bytes(USER_SOURCE.read_bytes())
    assert digest(COPY)==original_hash,'The archived copy differs from the supplied original'
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(COPY))
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    assert len(objects)==1,'Inspect unexpected multi-object input before editing'
    model=objects[0];model.name='Paladin_Meshy_Copia_Editable'
    # Normalize position and units once, without remeshing or changing faces.
    world=model.matrix_world.copy();points=[world@v.co for v in model.data.vertices]
    mn=Vector(tuple(min(p[i] for p in points) for i in range(3)))
    mx=Vector(tuple(max(p[i] for p in points) for i in range(3)))
    center=(mn+mx)*.5;scale=2.08/(mx.z-mn.z)
    for v,p in zip(model.data.vertices,points):v.co=((p.x-center.x)*scale,(p.y-center.y)*scale,(p.z-mn.z)*scale)
    model.matrix_world.identity();bpy.context.view_layer.update()
    collection=bpy.data.collections.new('01_Copia_original_editable');bpy.context.scene.collection.children.link(collection)
    for old in list(model.users_collection):old.objects.unlink(model)
    collection.objects.link(model)
    uv_before=uv_digest(model.data);topology_before=topology_digest(model.data)
    used_images={node.image for mat in model.data.materials for node in mat.node_tree.nodes
                 if node.type=='TEX_IMAGE' and node.image}
    source_images={im.name:image_digest(im) for im in used_images}
    assert len(source_images)==3
    basis=[v.co.copy() for v in model.data.vertices]
    model.shape_key_add(name='00_Original_normalizado',from_mix=False)
    keys=edits(model,basis)
    model['source_original']=str(COPY);model['source_sha256']=original_hash
    model['workflow']='Direct proportional mesh edits with independent shape keys; original UV and topology'
    model['license']='CC BY 4.0 per project source record'
    model['pose']='Original T-pose; static mesh without skeleton'
    assert uv_digest(model.data)==uv_before and topology_digest(model.data)==topology_before
    camera=setup_studio();bpy.ops.file.pack_all();configure_view(model)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    depsgraph=bpy.context.evaluated_depsgraph_get();evaluated=model.evaluated_get(depsgraph)
    data=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=depsgraph)
    frozen=bpy.data.objects.new('Paladin_Meshy_Elite_Edit',data);collection.objects.link(frozen)
    bpy.ops.object.select_all(action='DESELECT');frozen.select_set(True);bpy.context.view_layer.objects.active=frozen
    bpy.ops.export_scene.gltf(filepath=str(EXPORT),export_format='GLB',use_selection=True,export_apply=True,export_morph=False)
    result=validate_export(model,frozen,source_images)
    distances=[(a.co-b).length for a,b in zip(frozen.data.vertices,basis)]
    bounds=[v.co for v in frozen.data.vertices]
    report={'source_original':str(USER_SOURCE),'archived_copy':str(COPY),'source_sha256':original_hash,
            'original_and_copy_identical':True,'vertices_editable':len(model.data.vertices),
            'triangles':len(model.data.polygons),'uv_hash_before':uv_before,'uv_hash_after':uv_digest(model.data),
            'topology_hash_before':topology_before,'topology_hash_after':topology_digest(model.data),
            'uv_and_connectivity_preserved':True,'source_images_sha256':source_images,
            'shape_keys':[k.name for k in keys],'moved_vertices':sum(d>.00001 for d in distances),
            'max_displacement_m':max(distances),'dimensions_m':[max(p[i] for p in bounds)-min(p[i] for p in bounds) for i in range(3)],
            'export_validation':result,'pose':'Original T-pose','rig':False,
            'stage':'First direct modification of the source mesh; artistic review and animation preparation pending'}
    (OUT/'validation_direct_edit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    bpy.data.objects.remove(frozen,do_unlink=True)
    scene=bpy.context.scene
    for title,loc in [('TresCuartos',(2.7,-5.8,2.6)),('Frente',(0,-6,1.13)),('Espalda',(-2.7,5.8,2.6))]:
        camera.location=loc;look_at(camera,(0,0,1.045))
        scene.render.filepath=str(OUT/f'Preview/Paladin_Meshy_Edit_{title}.png')
        bpy.ops.render.render(write_still=True)
    camera.location=(2.7,-5.8,2.6);look_at(camera,(0,0,1.045))
    for key in keys:key.value=0
    scene.render.filepath=str(OUT/'Preview/Paladin_Meshy_Original_Comparacion.png')
    bpy.ops.render.render(write_still=True)
    for key in keys:key.value=1
    assert digest(USER_SOURCE)==original_hash and digest(COPY)==original_hash,'The source changed during the task'
    print('DIRECT_EDIT_COMPLETE='+json.dumps(report),flush=True)


if __name__=='__main__':main()
