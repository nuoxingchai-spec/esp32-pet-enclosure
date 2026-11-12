import bpy, bmesh
from mathutils import Vector

BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world; mi = mw.inverted(); M3i = mw.to_3x3().inverted()
dg = bpy.context.evaluated_depsgraph_get()

def stats(bm, tag):
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    nm = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    bnd = sum(1 for e in bm.edges if len(e.link_faces) < 2)
    zero = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
    vol = bm.calc_volume(signed=True)
    lens = sorted(e.calc_length() for e in bm.edges)
    print(f"CLEAN {tag:6s} v={len(bm.verts)} f={len(bm.faces)} nm={nm} bnd={bnd} zero={zero} vol={vol:.4f} "
          f"min={lens[0]:.8f} lt100nm={sum(1 for l in lens if l < 1e-4)} lt1um={sum(1 for l in lens if l < 1e-3)}")

bm = bmesh.new(); bm.from_mesh(body.data)
stats(bm, 'BEFORE')
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges)
stats(bm, 'AFTER')
bm.to_mesh(body.data)
bm.free()
for p in body.data.polygons:
    p.use_smooth = False
body.data.update()

def cast(sx, y, z):
    org = mi @ Vector((sx * 60.0, y, z))
    d = (M3i @ Vector((-sx, 0.0, 0.0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=200.0, depsgraph=dg)
    if not ok: return None
    return (mw @ loc).x * sx
print('--- seam flush after clean ---')
worst = 0.0
for sx in (1, -1):
    for y in (30.0, 35.3, 45.0, -30.0, -35.3, -45.0):
        lo = cast(sx, y, 54.20); up = cast(sx, y, 54.55)
        d = (lo - up) * 1000.0
        worst = max(worst, abs(d))
        print(f"  sx={sx:+d} y={y:6.1f} d={d:6.2f}um")
print(f"SEAM-WORST {worst:.2f}um")
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('SAVED', BLEND)
