"""Read-only geometric diagnostics for the supplied normal paladin."""
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/Characters/Enemies/PaladinElite/Diagnostics'
BASE = ROOT / 'Assets/Characters/Enemies/Paladin/Source/PaladinSoldier_Meshy_Source.glb'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(BASE))
objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
raw = [obj.matrix_world @ vert.co for obj in objects for vert in obj.data.vertices]
minimum = Vector(tuple(min(p[i] for p in raw) for i in range(3)))
maximum = Vector(tuple(max(p[i] for p in raw) for i in range(3)))
center = (minimum + maximum) * .5
scale = 2.08 / (maximum.z - minimum.z)
points = [Vector(((p.x-center.x)*scale, (p.y-center.y)*scale, (p.z-minimum.z)*scale)) for p in raw]

def stats(pts):
    if not pts:
        return {'count': 0}
    mn = [min(p[i] for p in pts) for i in range(3)]
    mx = [max(p[i] for p in pts) for i in range(3)]
    return {'count': len(pts), 'min': [round(v,4) for v in mn], 'max': [round(v,4) for v in mx], 'bbox_center': [round((a+b)/2,4) for a,b in zip(mn,mx)], 'mean': [round(sum(p[i] for p in pts)/len(pts),4) for i in range(3)]}

arm_slices = []
for step in range(14):
    lo = .28 + step*.04
    hi = lo+.04
    pts = [p for p in points if lo <= abs(p.x) < hi and p.z > 1.35]
    folded = [Vector((abs(p.x),p.y,p.z)) for p in pts]
    arm_slices.append({'abs_x_range': [round(lo,2),round(hi,2)], **stats(folded)})

leg_slices = []
for step in range(23):
    lo = step*.04
    hi = lo+.04
    pts = [Vector((abs(p.x),p.y,p.z)) for p in points if lo <= p.z < hi and abs(p.x)>.04]
    leg_slices.append({'z_range': [round(lo,2),round(hi,2)], **stats(pts)})

hands = [p for p in points if abs(p.x)>.69 and p.z>1.35]
def warp(p, stretch=False):
    p=p.copy()
    side=1 if p.x>=0 else -1
    ax=abs(p.x)
    if p.z>1.37 and ax>.24:
        t=max(0,min(1,(ax-.24)/.11));t=t*t*(3-2*t)
        angle=math.radians(67)*t
        dx=ax-.28+(max(0,ax-.42)*.52 if stretch else 0)
        dz=p.z-1.64
        p.x=side*(.325+dx*math.cos(angle)+dz*math.sin(angle))
        p.z=1.69-dx*math.sin(angle)+dz*math.cos(angle)
    else:
        p.x*=1.16 if p.z>1.05 else .94
    p.y*=1.12
    return Vector((abs(p.x),p.y,p.z))

report={'normalized_height_m':2.08, 'source_bounds':stats(points), 'arm_slices':arm_slices,'leg_slices':leg_slices,'hand_region_abs_x_over_069':stats([Vector((abs(p.x),p.y,p.z)) for p in hands]), 'hand_warp_original':stats([warp(p) for p in hands]), 'hand_warp_stretched':stats([warp(p,True) for p in hands])}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'base_geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('ELITE_BASE_DIAGNOSTICS='+json.dumps(report))
