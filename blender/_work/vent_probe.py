import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage5b.blend")
lid = bpy.data.objects['Enclosure_Lid']
bm = bmesh.new(); bm.from_mesh(lid.data); bm.transform(lid.matrix_world)
t = BVHTree.FromBMesh(bm); bm.free()

def scan(x):
    runs=[]; inside=False; y0=None; lastz=None
    y=-62.0
    while y<=62.0:
        loc,nor,idx,d = t.ray_cast(Vector((x,y,80)), Vector((0,0,-1)), 100)
        hole = (loc is None) or (loc.z < 66.5)
        if hole and not inside: inside=True; y0=y
        if not hole and inside:
            inside=False; runs.append((round(y0,1), round(y-0.5,1)))
        y+=0.5
    if inside: runs.append((round(y0,1),62.0))
    print(f'x={x:5.1f} holes y-runs:', runs)
for x in (0.0, 8.0, 16.0, 17.0, 18.0, 21.0, 25.0):
    scan(x)
print('DONE')
