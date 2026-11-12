import bpy, bmesh, os
from mathutils import Vector

ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, r"blender\_work\rev13_smooth.blend"))
lid = bpy.data.objects['Enclosure_Lid']
mw = lid.matrix_world
bm = bmesh.new(); bm.from_mesh(lid.data)
bm.edges.ensure_lookup_table(); bm.verts.ensure_lookup_table()
bad = [e for e in bm.edges if len(e.link_faces) != 2]
print('bad edges', len(bad))
for e in bad:
    a, b = e.verts
    pa, pb = mw @ a.co, mw @ b.co
    print(f"  edge len={e.calc_length():.6f} nfaces={len(e.link_faces)} "
          f"a=({pa.x:.4f},{pa.y:.4f},{pa.z:.4f}) b=({pb.x:.4f},{pb.y:.4f},{pb.z:.4f})")
    for v in (a, b):
        near = [w for w in bm.verts if w != v and (w.co - v.co).length < 0.05]
        print(f"    vert ({v.co.x:.4f},{v.co.y:.4f},{v.co.z:.4f}) near={len(near)}")
        for w in near:
            print(f"      near ({w.co.x:.4f},{w.co.y:.4f},{w.co.z:.4f}) d={(w.co-v.co).length:.6f}")
    for f in e.link_faces:
        c = mw @ f.calc_center_median()
        print(f"    face area={f.calc_area():.8f} center=({c.x:.3f},{c.y:.3f},{c.z:.3f})")
# also count tiny edges / degenerate faces
tiny = [e for e in bm.edges if 0 < e.calc_length() < 1e-4]
print('tiny edges <1e-4:', len(tiny))
for e in tiny[:10]:
    print('   tiny', e.calc_length(), tuple(round(v,4) for v in (mw @ e.verts[0].co)))
bm.free()
print('DONE')
