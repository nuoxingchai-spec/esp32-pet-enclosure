import bpy, bmesh, os
from mathutils import Vector
path = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\stl\v3\Enclosure_Lid.stl"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=path, global_scale=1.0)
o = bpy.context.selected_objects[0]
bm = bmesh.new(); bm.from_mesh(o.data)
print('RAW v', len(bm.verts), 'f', len(bm.faces))
zero_raw = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
print('RAW zero-area faces', zero_raw)
for f in bm.faces:
    if f.calc_area() < 1e-10:
        c = sum((v.co for v in f.verts), Vector()) / len(f.verts)
        print('  ZERO at', tuple(round(x,3) for x in c), 'verts', [tuple(round(x,3) for x in v.co) for v in f.verts])
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
bm.edges.ensure_lookup_table(); bm.verts.ensure_lookup_table()
bad = [e for e in bm.edges if len(e.link_faces) != 2]
print('WELDED v', len(bm.verts), 'f', len(bm.faces), 'bad edges', len(bad))
zs = {}
for e in bad:
    a, b = e.verts
    print(f"  BAD edge len={e.calc_length():.6f} faces={len(e.link_faces)} "
          f"A=({a.co.x:.3f},{a.co.y:.3f},{a.co.z:.3f}) B=({b.co.x:.3f},{b.co.y:.3f},{b.co.z:.3f})")
bm.free()
