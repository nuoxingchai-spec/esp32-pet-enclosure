import bpy, bmesh
from mathutils import Vector
print("FILE", bpy.data.filepath)
o = bpy.data.objects['Enclosure_Body'] if 'Enclosure_Body' in bpy.data.objects else bpy.context.selected_objects[0]
bm = bmesh.new()
bm.from_mesh(o.data)
if bpy.data.filepath.endswith('.stl'):
    pass
bm.edges.ensure_lookup_table()
lens = sorted(((e.calc_length(), i, e) for i, e in enumerate(bm.edges)), key=lambda t: (t[0], t[1]))
print("EDGES", len(bm.edges), "min", f"{lens[0][0]:.8f}")
print("SHORTEST", [f"{t[0]:.8f}" for t in lens[:10]])
print("COUNT<1e-5", sum(1 for t in lens if t[0] < 1e-5))
print("COUNT<1e-4", sum(1 for t in lens if t[0] < 1e-4))
print("COUNT<1e-3", sum(1 for t in lens if t[0] < 1e-3))
for l,_,e in lens[:8]:
    c = (e.verts[0].co + e.verts[1].co) / 2
    print(f"SHORTEDGE len={l:.8f} at ({c.x:.3f},{c.y:.3f},{c.z:.3f})")
nm = [e for e in bm.edges if len(e.link_faces) != 2]
print("NM", len(nm), "BND", sum(1 for e in bm.edges if len(e.link_faces) < 2))
for e in nm[:10]:
    c = (e.verts[0].co + e.verts[1].co) / 2
    print(f"NMEDGE len={e.calc_length():.8f} lf={len(e.link_faces)} at ({c.x:.3f},{c.y:.3f},{c.z:.3f})")
zt = [f for f in bm.faces if f.calc_area() < 1e-12]
print("ZERO", len(zt))
for f in zt[:10]:
    c = f.calc_center_median()
    print(f"ZFACE area={f.calc_area():.3e} nv={len(f.verts)} at ({c.x:.3f},{c.y:.3f},{c.z:.3f})")
bm.free()
print("DONE")
