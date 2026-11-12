import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
body = bpy.data.objects['Enclosure_Body']
bm = bmesh.new(); bm.from_mesh(body.data); bm.transform(body.matrix_world)
tb = BVHTree.FromBMesh(bm); bm.free()
def mat(x,y,z):
    o=Vector((-200,y,z)); dv=Vector((1,0,0)); n=0; last=-1e9; g=0
    while g<300:
        g+=1
        loc,nor,idx,dist=tb.ray_cast(o,dv,1000.0)
        if loc is None or loc.x>x: break
        if loc.x-last>0.2: n+=1; last=loc.x
        o=loc+dv*0.1
    return n%2==1
for x in (20,24,26,28,30,32,34,35,36):
    print(f"x={x} free y/z rows:")
    for y in (34,40,44,50,55):
        free=[]; run=None
        for i in range(200,451):
            z=i/10.0
            m=mat(x,y,z)
            if (not m) and run is None: run=z
            if m and run is not None: free.append((round(run,1),round(z-0.1,1))); run=None
        if run is not None: free.append((round(run,1),45.0))
        print(f"   y={y}: {free}")
