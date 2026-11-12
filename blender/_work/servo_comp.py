import bpy, bmesh
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage3.blend')
for name in ('SG90_Fit_1','SG90_Fit_2'):
    o=bpy.data.objects[name]; M=o.matrix_world
    bm=bmesh.new(); bm.from_mesh(o.data)
    seen=set(); comps=[]
    for v in bm.verts:
        if v.index in seen: continue
        st=[v]; comp=[]; seen.add(v.index)
        while st:
            a=st.pop(); comp.append(a)
            for e in a.link_edges:
                b=e.other_vert(a)
                if b.index not in seen:
                    seen.add(b.index); st.append(b)
        comps.append(comp)
    print(name, 'components', len(comps))
    for c in sorted(comps, key=len, reverse=True):
        ws=[M@v.co for v in c]
        xs=[p.x for p in ws]; ys=[p.y for p in ws]; zs=[p.z for p in ws]
        print(f'  verts {len(c):5d} x[{min(xs):6.2f},{max(xs):6.2f}] y[{min(ys):6.2f},{max(ys):6.2f}] z[{min(zs):6.2f},{max(zs):6.2f}]')
    bm.free()
