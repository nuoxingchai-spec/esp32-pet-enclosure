import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
body = bpy.data.objects['Enclosure_Body']
print("MW", body.matrix_world)
bm = bmesh.new(); bm.from_mesh(body.data); bm.transform(body.matrix_world)
t = BVHTree.FromBMesh(bm)
for org, d in [((0,200,45),(0,-1,0)), ((0,-200,45),(0,1,0)), ((-200,0,45),(1,0,0)), ((0,0,-100),(0,0,1))]:
    o=Vector(org); dv=Vector(d); n=0
    print("RAY", org, d)
    while n<12:
        ok, loc, nor, idx = t.ray_cast(o, dv, 1000.0)
        if not ok: break
        print("  hit", tuple(round(v,3) for v in loc), "dist", round((loc-o).length,3), "idx", idx)
        o = loc + dv*0.05
        n+=1
