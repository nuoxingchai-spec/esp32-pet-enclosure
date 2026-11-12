import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
def bvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
lo=bpy.data.objects['Enclosure_Lid']; bo=bpy.data.objects['Enclosure_Body']
T=bvh(lo); TB=bvh(bo)
bm=bmesh.new(); bm.from_mesh(lo.data); bm.transform(lo.matrix_world); bm.faces.ensure_lookup_table()
pairs=T.overlap(TB)
print("pairs",len(pairs))
cs=[bm.faces[i].calc_center_median() for i,j in pairs]
# cluster by quadrant and z
for qx in (1,-1):
    for qy in (1,-1):
        sel=[c for c in cs if c.x*qx>0 and c.y*qy>0]
        if sel:
            print(f"quad {qx:+d}{qy:+d} n={len(sel)} x[{min(c.x for c in sel):.2f},{max(c.x for c in sel):.2f}] y[{min(c.y for c in sel):.2f},{max(c.y for c in sel):.2f}] z[{min(c.z for c in sel):.2f},{max(c.z for c in sel):.2f}]")
zs=sorted(round(c.z,2) for c in cs)
print("z range", zs[0], zs[-1])
# nearest pairs: body face centroid too
bm.free()
