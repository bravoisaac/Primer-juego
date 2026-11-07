"""Rebake seven clips on the existing rig; preserve source mesh, skin, textures and original blend.
Run with installed Blender: --background --python Tools/Blender/polish_gilded_animations.py
"""
import bpy
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sentinel_motion import DURATIONS, set_pose

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'Assets/Characters/Enemies/GildedSentinel'
UNITY = ROOT / 'Unity/TenFe/Assets/Art/GildedSentinel'
bpy.ops.wm.open_mainfile(filepath=str(ART / 'Source/GildedSentinel_Rigged.blend'))
rig = bpy.data.objects['SentinelRig']
mesh = bpy.data.objects['SentinelBody']
sword = bpy.data.objects['SentinelSword']
rig.animation_data_clear()
for action in list(bpy.data.actions):
    bpy.data.actions.remove(action)
rig.animation_data_create()
for name, end in DURATIONS.items():
    action = bpy.data.actions.new(name)
    action.use_fake_user = True
    rig.animation_data.action = action
    # Per-frame authored samples avoid cubic overshoot at planted feet and strike contact.
    for frame in range(1, end + 2):
        set_pose(rig, name, (frame - 1) / end)
        for bone in rig.pose.bones:
            bone.keyframe_insert('rotation_quaternion', frame=frame, group=bone.name)
            bone.keyframe_insert('location', frame=frame, group=bone.name)

scene = bpy.context.scene
scene.render.fps = 30
rig.animation_data.action = bpy.data.actions['Idle']
scene.frame_set(1)
scene.frame_start, scene.frame_end = 1, 61
bpy.ops.object.select_all(action='DESELECT')
for obj in (rig, mesh, sword):
    obj.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.export_scene.fbx(filepath=str(UNITY / 'GildedSentinel.fbx'), use_selection=True,
    object_types={'ARMATURE', 'MESH'}, apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS',
    axis_forward='-Z', axis_up='Y', add_leaf_bones=False, bake_anim=True,
    bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False, bake_anim_simplify_factor=0,
    path_mode='STRIP', embed_textures=False)
bpy.ops.wm.save_as_mainfile(filepath=str(ART / 'Source/GildedSentinel_Animated.blend'))
report = {'animations': DURATIONS, 'fps': 30, 'vertices': len(mesh.data.vertices),
    'bones': len(rig.data.bones), 'source_sha256': hashlib.sha256((ART / 'Source/GildedSentinel_Original.glb').read_bytes()).hexdigest(),
    'changes': ['two-link leg solve and level ankles', 'stance/swing timing with toe clearance',
        'continuous windup-to-strike pose', 'follow-through and eased recovery', 'fast recoil', 'knees buckle before falling'],
    'limits': ['approximate existing skin weights', 'no runtime ground IK', 'manual artistic review pending']}
(ART / 'animation-polish.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('TENFE_ANIMATION_POLISH ' + json.dumps(report))
