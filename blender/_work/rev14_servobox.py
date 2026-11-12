import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
body = bpy.data.objects['Enclosure_Body']
bm = bmesh.new(); bm.from_mesh(body.data); bm.transform(body.matrix_world)
tb = BVHTree.FromBMesh(bm); bm.free()
def box_test(label, x0,x1,y0,y1,z0,z1, shrink=0.0):
    bm2 = bmesh.new()
    bmesh.ops.create_cube(bm2, size=1.0)
    for v in bm2.verts:
        v.co.x = x0+shrink + (v.co.x+0.5)*((x1-x0)-2*shrink)
        v.co.y = y0+shrink + (v.co.y+0.5)*((y1-y0)-2*shrink)
        v.co.z = z0+shrink + (v.co.z+0.5)*((z1-z0)-2*shrink)
    t2 = BVHTree.FromBMesh(bm2); bm2.free()
    n = len(tb.overlap(t2))
    print(f"{label:22s} shrink={shrink:4.2f} overlap={n}")
for sx,sy in ((1,1),(1,-1),(-1,1),(-1,-1)):
    X = (14.1,36.6) if sx>0 else (-36.6,-14.1)
    Y = (32.6,55.4) if sy>0 else (-55.4,-32.6)
    for s in (0.0,0.2,0.4):
        box_test(f"SG90 body {sx:+d}{sy:+d}", X[0],X[1],Y[0],Y[1],31.9,44.1, s)
# slot opening vertical extent at x=32 (inside bay block) along y=44: material z spans free
print("BAY slot vertical free span at x=32:")
for y in (34,40,44,50,55):
    free=[]; run=None
    for i in range(200,451,1):
        z=i/10.0
        # material test along +X at this y,z: count hits before x=32
        o=Vector((-200,y,z)); dv=Vector((1,0,0)); n=0; last=-1e9; g=0
        while g<200:
            g+=1
            loc,nor,idx,dist=tb.ray_cast(o,dv,1000.0)
            if loc is None or loc.x>x: break
            if loc.x-last>0.2: n+=1; last=loc.x
            o=loc+dv*0.1
        m=n%2==1
        if (not m) and run is None: run=z
        if m and run is not None: free.append((run,z-0.1)); run=None
    if run is not None: free.append((run,45.0))
    print(f"  y={y}: free z {[(round(a,1),round(b,1)) for a,b in free if b-a>=0.2]}")
