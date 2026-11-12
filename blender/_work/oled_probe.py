import bpy, bmesh
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage3.blend')
for o in bpy.data.objects:
    if o.type=='MESH' and ('OLED' in o.name or 'Display' in o.name or 'Screen' in o.name):
        M=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data)
        seen=set(); comps=[]
        for v in bm.verts:
            if v.index in seen: continue
            st=[v]; comp=[]; seen.add(v.index)
            while st:
                a=st.pop(); comp.append(a)
                for e in a.link_edges:
                    b=e.other_vert(a)
                    if b.index not in seen: seen.add(b.index); st.append(b)
            comps.append(comp)
        print(o.name, 'comps', len(comps), 'mats', [m.name for m in o.data.materials])
        for c in sorted(comps,key=len,reverse=True)[:8]:
            ws=[M@v.co for v in c]; xs=[p.x for p in ws]; ys=[p.y for p in ws]; zs=[p.z for p in ws]
            print(f'  {len(c):5d} verts x[{min(xs):.2f},{max(xs):.2f}] y[{min(ys):.2f},{max(ys):.2f}] z[{min(zs):.2f},{max(zs):.2f}]')
        bm.free()
