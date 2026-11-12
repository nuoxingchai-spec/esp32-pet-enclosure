import bpy, bmesh, os
STL = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\stl\v3\Enclosure_Body.stl"
for dist in (0.0, 1e-9, 1e-7, 1e-5, 1e-4, 1e-3, 1e-2):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=STL, global_scale=1.0)
    o = bpy.context.selected_objects[0]
    bm = bmesh.new(); bm.from_mesh(o.data)
    if dist > 0:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    nm = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    bnd = sum(1 for e in bm.edges if len(e.link_faces) < 2)
    zero = sum(1 for f in bm.faces if f.calc_area() < 1e-12)
    vol = bm.calc_volume(signed=True)
    print(f"WELD {dist:g} v={len(bm.verts)} f={len(bm.faces)} nm={nm} bnd={bnd} zero={zero} vol={vol:.1f}")
    if dist == 1e-9:
        lens = sorted(e.calc_length() for e in bm.edges)
        print("  minlen", [f"{x:.6f}" for x in lens[:12]])
        short = [e for e in bm.edges if len(e.link_faces) < 2]
        for e in short[:6]:
            c = e.calc_center_median()
            print(f"  BND edge len={e.calc_length():.6f} at ({c.x:.3f},{c.y:.3f},{c.z:.3f})")
        for e in [e for e in bm.edges if len(e.link_faces) > 2][:3]:
            c = e.calc_center_median()
            print(f"  NM edge len={e.calc_length():.6f} at ({c.x:.3f},{c.y:.3f},{c.z:.3f})")
        zt = [f for f in bm.faces if f.calc_area() < 1e-12]
        for f in zt[:6]:
            c = f.calc_center_median()
            print(f"  ZTRI at ({c.x:.3f},{c.y:.3f},{c.z:.3f}) area={f.calc_area():.3e} nv={len(f.verts)}")
    bm.free()
print('DONE')
