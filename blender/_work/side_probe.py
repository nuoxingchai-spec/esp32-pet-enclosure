import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage5b.blend")
o=bpy.data.objects['Enclosure_Body']
bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
t=BVHTree.FromBMesh(bm)
for y in (-35.47,-42.45,-49.47):
    for dz in (0.0, 1.0, 2.0):
        z=57.2+dz
        loc,nor,idx,d=t.ray_cast(Vector((-100,y,z)),Vector((1,0,0)),200)
        print('RAY', y, z, tuple(round(v,3) for v in loc) if loc else None, 'normal', tuple(round(v,2) for v in nor) if nor else None)
# also from inside out
for y in (-35.47,-42.45,-49.47):
    loc,nor,idx,d=t.ray_cast(Vector((-30,y,57.2)),Vector((-1,0,0)),200)
    print('RAYOUT', y, tuple(round(v,3) for v in loc) if loc else None)
bm.free()
print('DONE')
