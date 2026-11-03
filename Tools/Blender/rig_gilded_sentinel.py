"""Build a separate, editable gameplay rig from the user-provided Meshy GLB.

No external downloads. Source remains byte-identical. This is a prototype skin,
not production retopology: armor deformation still needs artistic review.
"""
import bpy
import json
import math
import hashlib
from pathlib import Path
from mathutils import Vector, Quaternion
import numpy as np

ROOT = Path(r"C:\Users\isaac\Documents\Proyectos\Ten Fe")
ART = ROOT / "Assets/Characters/Enemies/GildedSentinel"
UNITY = ROOT / "Unity/TenFe/Assets/Art/GildedSentinel"
SOURCE = ART / "Source/GildedSentinel_Original.glb"


def bounds(obj):
    points = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    return Vector(tuple(min(p[i] for p in points) for i in range(3))), Vector(tuple(max(p[i] for p in points) for i in range(3)))


def world_rotation(bone, axis, degrees):
    local_axis = bone.bone.matrix_local.to_3x3().inverted() @ Vector(axis)
    return Quaternion(local_axis, math.radians(degrees))


def set_pose(rig, kind, t):
    for bone in rig.pose.bones:
        bone.rotation_mode = 'QUATERNION'
        bone.rotation_quaternion = Quaternion()
        bone.location = (0, 0, 0)
    def turn(name, axis, deg):
        p = rig.pose.bones[name]
        p.rotation_quaternion = p.rotation_quaternion @ world_rotation(p, axis, deg)
    def arm(side, drop=64, forward=0, bend=12):
        sign = 1 if side == 'L' else -1
        turn('UpperArm.' + side, (0, 1, 0), sign * drop)
        turn('UpperArm.' + side, (1, 0, 0), forward)
        turn('Forearm.' + side, (0, 0, 1), -sign * bend)
    arm('L', 63, -8, 22)
    arm('R', 62, 2, 16)
    if kind == 'Idle':
        breath = math.sin(t * math.tau)
        turn('Chest', (1, 0, 0), breath * 1.5)
        turn('Head', (0, 0, 1), breath * 1.8)
    elif kind in ('Walk', 'Run'):
        sine = math.sin(t * math.tau)
        amp = 20 if kind == 'Walk' else 32
        for side, sign in [('L', 1), ('R', -1)]:
            swing = sine * sign
            turn('Thigh.' + side, (1, 0, 0), swing * amp)
            turn('Shin.' + side, (1, 0, 0), -max(0, -swing) * (28 if kind == 'Walk' else 50))
            turn('Foot.' + side, (1, 0, 0), max(0, -swing) * 12)
            turn('UpperArm.' + side, (1, 0, 0), -swing * amp * .4)
        turn('Hips', (0, 0, 1), sine * 3)
        turn('Chest', (0, 0, 1), -sine * 5)
        turn('Chest', (1, 0, 0), 6 if kind == 'Run' else 2)
        # Local hip Y is vertical; keep foot penetration small and root motion off.
        rig.pose.bones['Hips'].location.y = -abs(sine) * .018
    elif kind == 'Windup':
        blend = t * t * (3 - 2 * t)
        turn('UpperArm.R', (0, 1, 0), 85 * blend)
        turn('UpperArm.R', (0, 0, 1), 35 * blend)
        turn('Forearm.R', (0, 0, 1), 55 * blend)
        turn('Chest', (0, 0, 1), -24 * blend)
        turn('Head', (0, 0, 1), 16 * blend)
        turn('Thigh.L', (1, 0, 0), 10 * blend)
    elif kind == 'Strike':
        # Impact at t=.14 (0.16s). Recover to the ready pose after the follow-through.
        if t <= .14:
            b = t / .14
            raise_arm, twist, bend, chest = 85 * (1-b) - 12*b, 35*(1-b) - 65*b, 55*(1-b), -24*(1-b)+20*b
        else:
            b = min(1, (t-.14)/.86)
            raise_arm, twist, bend, chest = -12*(1-b), -65*(1-b), 0, 20*(1-b)
        turn('UpperArm.R', (0, 1, 0), raise_arm)
        turn('UpperArm.R', (0, 0, 1), twist)
        turn('Forearm.R', (0, 0, 1), bend)
        turn('Chest', (0, 0, 1), chest)
    elif kind == 'Hit':
        amount = math.sin(t * math.pi)
        turn('Chest', (1, 0, 0), -14*amount)
        turn('Head', (1, 0, 0), -12*amount)
        turn('Hips', (0, 0, 1), 6*amount)
    elif kind == 'Death':
        b = t*t*(3-2*t)
        # Root tips the complete rig; feet and hips follow one coherent motion.
        turn('Root', (1, 0, 0), -86*b)
        rig.pose.bones['Root'].location.y = .13*b
        turn('Thigh.L', (1, 0, 0), 12*b)
        turn('Shin.L', (1, 0, 0), -22*b)
        turn('UpperArm.L', (0, 1, 0), -15*b)


def create_rig(mesh):
    bones = [
        ('Root', (0,0,0), (0,0,.2), None),
        ('Hips', (0,0,.97), (0,0,1.10), 'Root'),
        ('Spine', (0,0,1.10), (0,0,1.29), 'Hips'),
        ('Chest', (0,0,1.29), (0,0,1.51), 'Spine'),
        ('Neck', (0,0,1.51), (0,0,1.66), 'Chest'),
        ('Head', (0,0,1.66), (0,0,1.95), 'Neck'),
    ]
    for side, sign in [('L',1),('R',-1)]:
        def p(x,y,z): return (sign*x,y,z)
        bones.extend([
            ('Clavicle.'+side, p(.04,0,1.51), p(.25,0,1.50), 'Chest'),
            ('UpperArm.'+side, p(.25,0,1.50), p(.49,0,1.46), 'Clavicle.'+side),
            ('Forearm.'+side, p(.49,0,1.46), p(.68,-.015,1.44), 'UpperArm.'+side),
            ('Hand.'+side, p(.68,-.015,1.44), p(.80,-.015,1.42), 'Forearm.'+side),
            ('Thigh.'+side, p(.13,0,.97), p(.15,0,.54), 'Hips'),
            ('Shin.'+side, p(.15,0,.54), p(.15,0,.13), 'Thigh.'+side),
            ('Foot.'+side, p(.15,0,.13), p(.15,-.17,.065), 'Shin.'+side),
        ])
    arm = bpy.data.armatures.new('SentinelSkeleton')
    rig = bpy.data.objects.new('SentinelRig',arm); bpy.context.collection.objects.link(rig)
    bpy.context.view_layer.objects.active=rig; rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name,head,tail,parent in bones:
        bone=arm.edit_bones.new(name); bone.head=head; bone.tail=tail
        if parent: bone.parent=arm.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    coords=np.empty(len(mesh.data.vertices)*3); mesh.data.vertices.foreach_get('co',coords); coords=coords.reshape(-1,3)
    groups={name:mesh.vertex_groups.new(name=name) for name,_,_,_ in bones if name!='Root'}
    # Local distance weights constrained by anatomy, with max 4 influences. UV seams remain intact.
    defs={name:(np.array(head),np.array(tail)) for name,head,tail,_ in bones}
    for v,co in zip(mesh.data.vertices,coords):
        x,y,z=co; side='L' if x>=0 else 'R'; ax=abs(x)
        if z>1.62 and ax<.27:
            candidates=['Head','Neck'] if z<1.72 else ['Head']
        elif ax>.245 and z>1.29:
            candidates=['Clavicle.'+side,'UpperArm.'+side,'Forearm.'+side,'Hand.'+side]
            if ax<.32: candidates=['Chest','Clavicle.'+side,'UpperArm.'+side]
        elif z<1.04:
            candidates=['Thigh.'+side,'Shin.'+side,'Foot.'+side]
            if z>.78: candidates=['Hips','Thigh.'+side]
            if z>.84 and ax<.09: candidates=['Hips']
        else:
            candidates=['Hips','Spine','Chest','Neck']
        dist=[]
        for name in candidates:
            a,b=defs[name]; delta=b-a; along=np.clip(np.dot(co-a,delta)/np.dot(delta,delta),0,1)
            dist.append(np.linalg.norm(co-(a+along*delta)))
        distances=np.asarray(dist)
        weights=np.exp(-np.square(distances-distances.min())/(.055**2))
        weights[weights<.06]=0; weights/=weights.sum()
        for name,w in zip(candidates,weights):
            if w>0: groups[name].add([v.index],float(w),'REPLACE')
    mesh.parent=rig
    modifier=mesh.modifiers.new('Sentinel Skin','ARMATURE'); modifier.object=rig; modifier.use_deform_preserve_volume=False
    return rig


def export_textures(mesh):
    texture_dir=UNITY/'Textures'; texture_dir.mkdir(parents=True,exist_ok=True)
    material=mesh.data.materials[0]; material.name='SentinelSurface'
    result={}
    for node in material.node_tree.nodes:
        if node.type!='TEX_IMAGE' or not node.image: continue
        targets=[link.to_socket.name for out in node.outputs for link in out.links]
        types=[link.to_node.type for out in node.outputs for link in out.links]
        kind='BaseColor' if 'Base Color' in targets else 'Normal' if 'NORMAL_MAP' in types else 'ORM'
        image=node.image; image.name='Sentinel_'+kind
        image.filepath_raw=str(texture_dir/('Sentinel_'+kind+'.png')); image.file_format='PNG'; image.save()
        image.pack(); result[kind]=list(image.size)
        if kind=='ORM':
            data=np.array(image.pixels[:],dtype=np.float32).reshape(-1,4)
            converted=np.zeros_like(data); converted[:,0]=data[:,2]; converted[:,3]=1-data[:,1]
            out=bpy.data.images.new('Sentinel_MetallicSmoothness',width=image.size[0],height=image.size[1],alpha=True)
            out.colorspace_settings.name='Non-Color'; out.pixels.foreach_set(converted.ravel())
            out.filepath_raw=str(texture_dir/'Sentinel_MetallicSmoothness.png'); out.file_format='PNG'; out.save(); bpy.data.images.remove(out)
    return result


def add_weapon(rig):
    # Original simple sword skinned rigidly to the right hand, with grip at the palm.
    material=bpy.data.materials.new('SentinelWeapon'); material.diffuse_color=(.23,.25,.28,1); material.use_nodes=True
    shader=material.node_tree.nodes.get('Principled BSDF'); shader.inputs['Metallic'].default_value=.85; shader.inputs['Roughness'].default_value=.32
    pieces=[]
    for name,loc,scale in [
        ('Blade',(-.755,-.48,1.42),(.038,.38,.012)),
        ('Guard',(-.755,-.10,1.42),(.12,.018,.022)),
        ('Grip',(-.755,-.015,1.42),(.018,.07,.018)),
        ('Pommel',(-.755,.065,1.42),(.026,.026,.026))]:
        bpy.ops.mesh.primitive_cube_add(size=2,location=loc); ob=bpy.context.object; ob.name=name; ob.scale=scale
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True); ob.data.materials.append(material); pieces.append(ob)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in pieces: ob.select_set(True)
    bpy.context.view_layer.objects.active=pieces[0]; bpy.ops.object.join(); sword=bpy.context.object; sword.name='SentinelSword'
    sword.vertex_groups.new(name='Hand.R').add(list(range(len(sword.data.vertices))),1,'REPLACE')
    sword.parent=rig; modifier=sword.modifiers.new('Sword hand binding','ARMATURE'); modifier.object=rig
    return sword


def preview(rig, action, path, frame=1, camera_pos=(3,-4,2.5)):
    rig.animation_data.action=bpy.data.actions[action]; bpy.context.scene.frame_set(frame)
    scene=bpy.context.scene
    scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=True
    scene.render.resolution_x=768; scene.render.resolution_y=768; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(path)
    scene.world.color=(.2,.2,.2)
    studio=[]
    bpy.ops.object.camera_add(location=camera_pos); cam=bpy.context.object; studio.append(cam)
    cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=2.7; scene.camera=cam
    for loc,power,color in [((2,-3,4),650,(1,.85,.68)),((-3,-1,2),500,(.6,.75,1)),((1,3,3),800,(1,.76,.45))]:
        bpy.ops.object.light_add(type='AREA',location=loc); light=bpy.context.object; studio.append(light); light.data.energy=power; light.data.color=color; light.data.shape='DISK'; light.data.size=3
        light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.render.render(write_still=True)
    for obj in studio: bpy.data.objects.remove(obj,do_unlink=True)


def main():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(SOURCE))
    mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH'); mesh.name='SentinelBody'
    bpy.context.view_layer.objects.active=mesh
    lo,hi=bounds(mesh); mesh.scale*=2/(hi.z-lo.z)
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    lo,hi=bounds(mesh); mesh.location+=Vector((-(lo.x+hi.x)/2,-(lo.y+hi.y)/2,-lo.z))
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    source_triangles=len(mesh.data.polygons)
    texture_info=export_textures(mesh)
    modifier=mesh.modifiers.new('Gameplay reduction','DECIMATE'); modifier.ratio=55000/source_triangles; modifier.use_collapse_triangulate=True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    for poly in mesh.data.polygons: poly.use_smooth=True
    rig=create_rig(mesh); sword=add_weapon(rig)
    rig.animation_data_create(); scene=bpy.context.scene; scene.render.fps=30
    durations={'Idle':60,'Walk':36,'Run':24,'Windup':24,'Strike':35,'Hit':15,'Death':42}
    for name,end in durations.items():
        action=bpy.data.actions.new(name); action.use_fake_user=True; rig.animation_data.action=action
        for frame in sorted(set(range(1,end+2,3))|{1,end+1}):
            set_pose(rig,name,(frame-1)/end)
            for bone in rig.pose.bones:
                bone.keyframe_insert('rotation_quaternion',frame=frame,group=bone.name)
                bone.keyframe_insert('location',frame=frame,group=bone.name)
    rig.animation_data.action=bpy.data.actions['Idle']; scene.frame_set(1); scene.frame_start=1; scene.frame_end=61
    bpy.ops.object.select_all(action='DESELECT')
    for obj in [mesh,rig,sword]: obj.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.export_scene.fbx(filepath=str(UNITY/'GildedSentinel.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},
        apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',add_leaf_bones=False,
        bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,
        path_mode='STRIP',embed_textures=False)
    bpy.ops.wm.save_as_mainfile(filepath=str(ART/'Source/GildedSentinel_Rigged.blend'))
    report={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_triangles':source_triangles,
        'gameplay_triangles':len(mesh.data.polygons),'vertices':len(mesh.data.vertices),'bones':len(rig.data.bones),
        'unweighted_vertices':sum(not v.groups for v in mesh.data.vertices),'max_influences':max(len(v.groups) for v in mesh.data.vertices),
        'animations':durations,'textures':texture_info,'height_m':2,'license':'CC BY 4.0; original rig, animations and sword added locally',
        'limitations':['Approximate anatomical weights; not manual production retopology','No individual finger rig or cloth simulation','Original authored prototype animation, not motion capture']}
    (ART/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('TENFE_SENTINEL_RIG '+json.dumps(report))
    for name,frame in [('Idle',1),('Walk',10),('Windup',25),('Strike',7)]:
        preview(rig,name,ART/'Preview'/f'{name}.png',frame)


if __name__=='__main__': main()
