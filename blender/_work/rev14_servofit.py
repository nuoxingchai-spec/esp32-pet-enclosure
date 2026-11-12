import bpy, bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
body = bpy.data.objects['Enclosure_Body']
bm = bmesh.new(); bm.from_mesh(body.data); bm.transform(body.matrix_world)
tb = BVHTree.FromBMesh(bm); bm.free()
for name in ('SG90_Fit_1','SG90_Fit_2','SG90_Fit_3','SG90_Fit_4'):
    o = bpy.data.objects[name]
    ctr = sum((o.matrix_world @ Vector(c) for c in o.bound_box), Vector())/8
    print(name, "center", tuple(round(v,2) for v in ctr))
    for s in (1.0, 0.995, 0.99, 0.98, 0.95, 0.90):
        bm2 = bmesh.new(); bm2.from_mesh(o.data)
        for v in bm2.verts:
            w = o.matrix_world @ v.co
            w = ctr + Vector(((w.x-ctr.x)*s, (w.y-ctr.y)*s, (w.z-ctr.z)*s))
            v.co = w
        t2 = BVHTree.FromBMesh(bm2); bm2.free()
        n = len(tb.overlap(t2))
        print(f"   scale {s:5.3f}  overlap faces={n}")
