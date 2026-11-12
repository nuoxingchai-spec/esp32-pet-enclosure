import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
def bvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
face=bvh(bpy.data.objects['Face_Plate'])
print("FACEPLATE first-hit y from +Y (direction -Y):")
for z in (25.5,54.5,30,45,50):
    line=[]
    for x in range(-23,24,1):
        loc,nor,idx,dist=face.ray_cast(Vector((x,200,z)),Vector((0,-1,0)),300.0)
        line.append('.' if loc is None else '#')
    print(f"z={z:5.1f} " + "".join(line))
print("FACEPLATE z scan at x=-20.8/+20.8")
for x in (-20.8,20.8,0):
    col=[]
    for z in range(21,60,1):
        loc,nor,idx,dist=face.ray_cast(Vector((x,200,z)),Vector((0,-1,0)),300.0)
        col.append('.' if loc is None else '#')
    print(f"x={x:6.1f} " + "".join(col))
pan=bvh(bpy.data.objects['Belly_Pan'])
print("PAN thickness/hole at x=20,y=48:", pan.ray_cast(Vector((20,48,-50)),Vector((0,0,1)),100.0)[0])
print("PAN solid at x=0,y=0:", pan.ray_cast(Vector((0,0,-50)),Vector((0,0,1)),100.0)[0])
