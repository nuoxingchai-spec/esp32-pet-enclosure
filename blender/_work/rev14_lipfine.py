import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
def tb(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
B=tb(bpy.data.objects['Enclosure_Body']); L=tb(bpy.data.objects['Enclosure_Lid'])
def mat(t,x,y,z):
    o=Vector((-200.0,y,z)); d=Vector((1,0,0)); n=0; last=-1e9; g=0
    while g<300:
        g+=1
        loc,nor,idx,dist=t.ray_cast(o,d,1000.0)
        if loc is None or loc.x>x: break
        if loc.x-last>0.2: n+=1; last=loc.x
        o=loc+d*0.1
    return n%2==1
def edges(t,y,z):
    prev=None; out=[]
    for i in range(330,410):
        x=i/10
        m=mat(t,x,y,z)
        if prev is not None and m!=prev: out.append(round(x,2))
        prev=m
    return out
for z in (58.8,58.9,59.0,59.2,59.5,59.8,59.9,60.0,60.1):
    print(f"z={z:5.1f} BODY edges {edges(B,0,z)}  LID edges {edges(L,0,z)}")
for y in (0,30,55,60,-40):
    print(f"y={y:4d} z=59.5 BODY {edges(B,y,59.5)} LID {edges(L,y,59.5)}")
for x in (34.5,35.5,36.5,37.5):
    # vertical edges along z at x fixed, y=0
    prev=None; out=[]
    for i in range(580,610):
        z=i/10; m=mat(B,x,0,z)
        if prev is not None and m!=prev: out.append(round(z,2))
        prev=m
    prev=None; outl=[]
    for i in range(580,610):
        z=i/10; m=mat(L,x,0,z)
        if prev is not None and m!=prev: outl.append(round(z,2))
        prev=m
    print(f"x={x} BODY z-edges {out} LID z-edges {outl}")
