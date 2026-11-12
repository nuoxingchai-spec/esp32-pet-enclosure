import bpy, bmesh, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage5b.blend")

def bvh(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    t = BVHTree.FromBMesh(bm); bm.free(); return t

ring = bpy.data.objects['LED_Diffuser_Ring']; tr = bvh(ring)
print('=== RING rear band scan (ray down from z80) ===')
for x in (-7.0, 0.0, 7.0):
    runs=[]; inside=False; y0=None
    y=-64.0
    while y<=-40.0:
        loc,nor,idx,d = tr.ray_cast(Vector((x,y,80)), Vector((0,0,-1)), 100)
        hit = loc is not None
        if hit and not inside: inside=True; y0=y
        if not hit and inside: inside=False; runs.append((y0, y-0.5))
        y+=0.5
    if inside: runs.append((y0,-40.0))
    print(f'x={x:5.1f} rear-band y-runs {[(round(a,1),round(b,1)) for a,b in runs]}')
for y in (-52.0,-52.5,-53.0,-53.5,-54.0):
    loc,nor,idx,d = tr.ray_cast(Vector((0,y,80)), Vector((0,0,-1)), 100)
    print(f'ring x0 y={y}: top z={loc.z:.3f}' if loc else f'ring x0 y={y}: none')
# inner edge of rear band at x0: front face y where material begins; also ring underside
print('=== RING inner front face / lid top gap ===')

tail = bpy.data.objects['Tail']; tt = bvh(tail)
print('=== TAIL lowest surface vs ring top (ray up x0) ===')
for y in [x*0.5 for x in range(-116,-96)]:
    loc,nor,idx,d = tt.ray_cast(Vector((0,y,50)), Vector((0,0,1)), 100)
    rr,_,_,_ = tr.ray_cast(Vector((0,y,80)), Vector((0,0,-1)), 100)
    print(f'y={y:6.1f} tail_bottom={loc.z:6.2f}  ring_top={rr.z if rr else None}')

# Tail radial profile: max |x| at each y (vertex sample)
print('=== TAIL x extent by y slice ===')
bm = bmesh.new(); bm.from_mesh(tail.data); bm.transform(tail.matrix_world)
buckets = {}
for v in bm.verts:
    k = round(v.co.y*2)/2
    buckets.setdefault(k, [0,0,1e9,-1e9])
    b = buckets[k]; b[0]=max(b[0],v.co.x); b[1]=min(b[1],v.co.x); b[2]=min(b[2],v.co.z); b[3]=max(b[3],v.co.z)
for k in sorted(buckets):
    if -57 <= k <= -49:
        b=buckets[k]; print(f'y={k:6.1f} x[{b[1]:5.2f},{b[0]:5.2f}] z[{b[2]:6.2f},{b[3]:6.2f}]')
bm.free()

# PCB components near rear-left button 3
pc = bpy.data.objects['PCB_Components']
bm = bmesh.new(); bm.from_mesh(pc.data); bm.transform(pc.matrix_world)
bm.verts.ensure_lookup_table()
parent=list(range(len(bm.verts)))
def find(a):
    while parent[a]!=a:
        parent[a]=parent[parent[a]]; a=parent[a]
    return a
for e in bm.edges:
    a,b=find(e.verts[0].index),find(e.verts[1].index)
    if a!=b: parent[a]=b
comps={}
for v in bm.verts:
    r=find(v.index); c=comps.setdefault(r,[[1e9,-1e9],[1e9,-1e9],[1e9,-1e9]])
    c[0][0]=min(c[0][0],v.co.x); c[0][1]=max(c[0][1],v.co.x)
    c[1][0]=min(c[1][0],v.co.y); c[1][1]=max(c[1][1],v.co.y)
    c[2][0]=min(c[2][0],v.co.z); c[2][1]=max(c[2][1],v.co.z)
print('=== PCB islands near button zone ===')
near=[]
for r,c in comps.items():
    if c[0][0] < -19 and c[0][1] > -31 and c[1][0] < -45 and c[1][1] > -56:
        near.append(c)
for c in sorted(near, key=lambda c:-c[2][1]):
    print(f'x[{c[0][0]:7.2f},{c[0][1]:7.2f}] y[{c[1][0]:7.2f},{c[1][1]:7.2f}] z[{c[2][0]:6.2f},{c[2][1]:6.2f}]')
bm.free()

# Ear/tail flare lowest z (vertices below 67.2)
for name in ('Ear_R','Tail'):
    o=bpy.data.objects[name]; mw=o.matrix_world
    zs=[(mw@v.co).z for v in o.data.vertices if (mw@v.co).z<67.3]
    print(name,'min z',min(zs),'count below 67.0',sum(1 for z in zs if z<67.0))
print('DONE')
