import bpy, bmesh
from mathutils import Vector
from collections import defaultdict, Counter
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob=bpy.data.objects['Enclosure_Body']; mw=ob.matrix_world
print('matrix_world:'); print(mw)
bm=bmesh.new(); bm.from_mesh(ob.data); bm.verts.ensure_lookup_table()
# world coordinate helper
def w(v): return mw @ v.co
# seam edges in world z=54.35
seam=[]
for e in bm.edges:
    a=w(e.verts[0]); b=w(e.verts[1])
    if abs(a.z-54.35)<0.03 and abs(b.z-54.35)<0.03:
        seam.append(e)
print('seam edges(world)',len(seam))
lens=[e.calc_length() for e in seam]
if lens: print('  len min/max',round(min(lens),3),round(max(lens),3))
# side wall seam near y=0: edges at z54.35 with |y|<50
side=[e for e in seam if abs(w(e.verts[0]).y)<50 and abs(w(e.verts[1]).y)<50]
print('  side-only edges',len(side))
if side:
    print('  sample',[(round(w(e.verts[0]).x,3),round(w(e.verts[0]).y,2),round(w(e.verts[0]).z,2)) for e in side[:5]])
    # adjacent faces normals
    import math
    ang=[]
    for e in side:
        fs=e.link_faces
        if len(fs)==2: ang.append(round(math.degrees(fs[0].normal.angle(fs[1].normal)),3))
    print('  side normals angle uniq',Counter(ang).most_common(5))
# corner verts world
vs=[v for v in bm.verts if w(v).x>38.3 and w(v).y<-55.5 and 45<w(v).z<56]
print('corner verts',len(vs))
for v in sorted(vs,key=lambda v:(round(w(v).z,2),round(w(v).y,2),round(w(v).x,2))):
    p=w(v); print(f'  v{v.index:5d} x{p.x:7.3f} y{p.y:7.3f} z{p.z:6.2f}')
# corner faces
fs=[f for f in bm.faces if all(w(v).x>37.8 and w(v).y<-55.0 and 45<w(v).z<56 for v in f.verts)]
print('corner faces',len(fs))
for f in fs:
    zs=sorted(set(round(w(v).z,2) for v in f.verts))
    xs=[round(w(v).x,2) for v in f.verts]; ys=[round(w(v).y,2) for v in f.verts]
    n=f.normal
    print(f'  f{f.index:5d} n({n.x:5.2f},{n.y:5.2f},{n.z:5.2f}) z{zs} x{xs} y{ys}')
bm.free()
