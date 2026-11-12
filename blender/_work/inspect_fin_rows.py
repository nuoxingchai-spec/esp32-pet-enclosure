import bpy, bmesh
from collections import Counter, defaultdict
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob=bpy.data.objects['Enclosure_Body']; mw=ob.matrix_world
bm=bmesh.new(); bm.from_mesh(ob.data); bm.verts.ensure_lookup_table()
def w(v): return mw @ v.co
# all verts in the rear-right corner sector
vs=[v for v in bm.verts if w(v).x>37.7 and w(v).y<-55.0]
print('corner sector verts',len(vs))
h=Counter(round(w(v).z,2) for v in vs)
print('z rows:',sorted(h.items()))
# fin vertical faces: faces in sector with z-span > 2
fs=[]
for f in bm.faces:
    zs=[w(v).z for v in f.verts]
    if max(zs)-min(zs)>2 and all(w(v).x>37.7 and w(v).y<-55.0 for v in f.verts):
        fs.append(f)
print('vertical faces',len(fs))
for f in fs[:40]:
    zs=sorted(set(round(w(v).z,2) for v in f.verts)); xs=sorted(set(round(w(v).x,2) for v in f.verts)); ys=sorted(set(round(w(v).y,2) for v in f.verts))
    print(f'  f{f.index} z{zs} x{xs} y{ys} n({f.normal.x:.2f},{f.normal.y:.2f},{f.normal.z:.2f})')
