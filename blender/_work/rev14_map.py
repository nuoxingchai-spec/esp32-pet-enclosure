import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
body = bpy.data.objects['Enclosure_Body']
bm = bmesh.new(); bm.from_mesh(body.data); bm.transform(body.matrix_world)
t = BVHTree.FromBMesh(bm)
def mat(x,y,z):
    o = Vector((-200,y,z)); dv=Vector((1,0,0)); n=0; last=-1e9; guard=0
    while guard < 200:
        guard += 1
        loc, nor, idx, dist = t.ray_cast(o, dv, 1000.0)
        if loc is None or loc.x > x: break
        if loc.x - last > 0.2: n += 1; last = loc.x
        o = loc + dv*0.1
    return n % 2 == 1
for z in (21, 25, 30, 38, 45, 50, 53.8, 55.5, 58, 59.8):
    print(f"Z={z}")
    for y in range(62,-64,-3):
        row=""
        for x in range(-40,41,2):
            row += "M" if mat(x,y,z) else "."
        print(f"{y:5d} {row}")
bm.free()
