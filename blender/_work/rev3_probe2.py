import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage5b.blend")

print('=== OBJECTS NEAR BUTTON 3 (-30..-18, -55..-45, z>55) ===')
for o in bpy.context.scene.objects:
    if o.type!='MESH' or o.hide_viewport: continue
    b=[o.matrix_world @ Vector(c) for c in o.bound_box]
    xs=[p.x for p in b]; ys=[p.y for p in b]; zs=[p.z for p in b]
    if max(xs)>-31 and min(xs)<-18 and max(ys)>-56 and min(ys)<-44 and max(zs)>55:
        print(f'{o.name:24s} x[{min(xs):7.2f},{max(xs):7.2f}] y[{min(ys):7.2f},{max(ys):7.2f}] z[{min(zs):6.2f},{max(zs):6.2f}]')

pc=bpy.data.objects['PCB_Components']
bm=bmesh.new(); bm.from_mesh(pc.data); bm.transform(pc.matrix_world)
bvh=BVHTree.FromBMesh(bm)
btn=bpy.data.objects['Button_Top_3']
bm2=bmesh.new(); bm2.from_mesh(btn.data); bm2.transform(btn.matrix_world)
best=(1e9,None,None)
bm.faces.ensure_lookup_table()
for v in bm2.verts:
    loc,nor,idx,d=bvh.find_nearest(v.co)
    if d<best[0]:
        f=bm.faces[idx]; best=(d,v.co.copy(),[tuple(round(c,2) for c in (vv.co)) for vv in f.verts])
print('NEAREST PCB face to Button_Top_3:', round(best[0],3), 'tailvert', tuple(round(c,2) for c in best[1]), 'faceverts', best[2])
bm2.free()
# component bboxes of PCB_Components overlapping the button zone, via edge islands
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
print('PCB islands:', len(comps))
near=[]
for r,c in comps.items():
    if c[0][0]<-18 and c[0][1]>-32 and c[1][0]<-44 and c[1][1]>-56 and c[2][1]>55:
        near.append(c)
for c in sorted(near,key=lambda c:-c[2][1])[:12]:
    print(f'  x[{c[0][0]:7.2f},{c[0][1]:7.2f}] y[{c[1][0]:7.2f},{c[1][1]:7.2f}] z[{c[2][0]:6.2f},{c[2][1]:6.2f}]')
bm.free()
print('DONE')
