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
def spans(vals, pred):
    out=[]; run=None
    for v in vals:
        m=pred(v)
        if (not m) and run is None: run=v
        if m and run is not None: out.append((round(run,1),round(v-0.1,1))); run=None
    if run is not None: out.append((round(run,1),round(vals[-1],1)))
    return [s for s in out if s[1]-s[0]>=0.2]
print("SLOT z at x=32,y=44:", spans([i/10 for i in range(200,601)], lambda z: mat(32,44,z)))
print("SLOT y at x=32,z=38:", spans([i/10 for i in range(250,651)], lambda y: mat(32,y,38)))
print("SLOT y at x=32,z=33.5:", spans([i/10 for i in range(250,651)], lambda y: mat(32,y,33.5)))
print("SLOT z at x=20,y=44:", spans([i/10 for i in range(200,601)], lambda z: mat(20,44,z)))
def box_test(label, x0,x1,y0,y1,z0,z1, sh=0.0):
    bm2=bmesh.new(); bmesh.ops.create_cube(bm2,size=1.0)
    for v in bm2.verts:
        v.co.x=x0+sh+(v.co.x+0.5)*((x1-x0)-2*sh)
        v.co.y=y0+sh+(v.co.y+0.5)*((y1-y0)-2*sh)
        v.co.z=z0+sh+(v.co.z+0.5)*((z1-z0)-2*sh)
    t2=BVHTree.FromBMesh(bm2); bm2.free()
    print(label, "overlap", len(tb.overlap(t2)))
for z0,z1 in ((31.9,44.1),(32.8,45.0),(32.4,44.6),(31.5,43.7)):
    box_test(f"body box z{z0}-{z1} sh0.2", 14.1,36.6,32.6,55.4,z0,z1,0.2)
