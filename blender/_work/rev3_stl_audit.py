import bpy, bmesh, os, glob
from mathutils import Vector

DIR = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\stl\v3"
files = sorted(glob.glob(os.path.join(DIR, '*.stl')))
print('FILES', len(files))
for path in files:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=path, global_scale=1.0)
    o = bpy.context.selected_objects[0]
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    parent = list(range(len(bm.verts)))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for e in bm.edges:
        a, b = find(e.verts[0].index), find(e.verts[1].index)
        if a != b: parent[a] = b
    comps = len({find(i) for i in range(len(bm.verts))})
    nm = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    bnd = sum(1 for e in bm.edges if len(e.link_faces) < 2)
    zero = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
    vol = bm.calc_volume(signed=True)
    bm.free()
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    xs=[p.x for p in bb]; ys=[p.y for p in bb]; zs=[p.z for p in bb]
    print(f"{os.path.basename(path):24s} v={len(o.data.vertices):6d} f={len(o.data.polygons):6d} comps={comps} nm={nm} bnd={bnd} zero={zero} vol={vol:10.1f}"
          f"  size {max(xs)-min(xs):7.2f}x{max(ys)-min(ys):7.2f}x{max(zs)-min(zs):7.2f}"
          f"  z[{min(zs):6.2f},{max(zs):6.2f}]")
print('DONE')
