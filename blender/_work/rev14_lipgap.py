import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
def tb(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
B=tb(bpy.data.objects['Enclosure_Body']); L=tb(bpy.data.objects['Enclosure_Lid'])
def spans(t,x,y,z):
    out=[]; run=None
    for i in range(-40,41):
        o=Vector((-40.0,y,z)); d=Vector((1,0,0))
        # material test at x=i
        oo=Vector((-200.0,y,z)); n=0; last=-1e9; g=0
        while g<200:
            g+=1
            loc,nor,idx,dist=t.ray_cast(oo,d,1000.0)
            if loc is None or loc.x>i: break
            if loc.x-last>0.2: n+=1; last=loc.x
            oo=loc+d*0.1
        m=n%2==1
        if (not m) and run is None: run=i
        if m and run is not None: out.append((run,i-1)); run=None
    if run is not None: out.append((run,40))
    return [s for s in out if s[1]>=s[0]]
for z in (58.9,59.3,59.7,59.9,60.0):
    for y in (0,40,-40,55):
        b=spans(B,0,y,z); l=spans(L,0,y,z)
        print(f"z={z} y={y:3d} BODY {b} LID {l}")
# nearest distances lid lip verts to body
bm=bmesh.new(); bm.from_mesh(bpy.data.objects['Enclosure_Lid'].data); bm.transform(bpy.data.objects['Enclosure_Lid'].matrix_world)
bm.verts.ensure_lookup_table()
low=[v.co for v in bm.verts if v.co.z<59.9]
best=1e9; bp=None
for p in low:
    loc,nor,idx,d=B.find_nearest(p)
    if loc is not None and d<best: best=d; bp=p
print("min lid-low vert to body", round(best,4), tuple(round(c,2) for c in bp) if bp else None)
bm.free()
