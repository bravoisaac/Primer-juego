import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Assets/Characters/Enemies/PaladinElite/DirectMesh/V2/Paladin_Meshy_Elite_V2.blend'))
ob=bpy.data.objects['Paladin_Meshy_Copia_Editable'];dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg)
mesh=bpy.data.meshes.new_from_object(ev,depsgraph=dg)
tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[p.vertices[:] for p in mesh.polygons])
report={'front_head':[],'hand_slices':[]}
for z in [1.83,1.86,1.89,1.92,1.95,1.97,2.00,2.03]:
    row={'z':z,'hits':[]}
    for x in [-.12,-.09,-.06,-.03,0,.03,.06,.09,.12]:
        hit=tree.ray_cast(Vector((x,-.6,z)),Vector((0,1,0)),1)
        row['hits'].append([x,round(hit[0].y,4) if hit[0] else None])
    report['front_head'].append(row)
for lo,hi in [(1.0,1.05),(1.05,1.10),(1.1,1.15),(1.15,1.2),(1.2,1.25),(1.25,1.3)]:
    ps=[v.co for v in mesh.vertices if .39<v.co.x<.7 and lo<v.co.z<hi]
    if ps:report['hand_slices'].append({'z':[lo,hi],'min':[min(p[i] for p in ps) for i in range(3)],'max':[max(p[i] for p in ps) for i in range(3)]})
print('PART_REPORT='+json.dumps(report),flush=True)
