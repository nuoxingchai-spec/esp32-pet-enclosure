import bpy, bmesh, math
from mathutils import Vector

P = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=P)
body = bpy.data.objects['Enclosure_Body']
bm = bmesh.new(); bm.from_mesh(body.data)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
ZL = 40.35
print("--- horizontal faces at seam, radius<43 (wall ledges) ---")
n = 0
for f in bm.faces:
    zs = [v.co.z for v in f.verts]
    if max(abs(z - ZL) for z in zs) > 0.002:
        continue
    if abs(f.normal.z) < 0.7:
        continue
    c = f.calc_center_median()
    r = math.hypot(c.x, c.y)
    if r > 43:
        continue
    n += 1
    vs = " ".join("(%.3f,%.3f,%.4f)" % (v.co.x, v.co.y, v.co.z) for v in f.verts)
    print("  r=%.3f a=%.6f nz=%.2f %s" % (r, f.calc_area(), f.normal.z, vs))
print("count", n)

# group by radial gap and bounds
print("--- non-horizontal faces adjacent to seam z=40.35, r<43 ---")
ids = set()
for f in bm.faces:
    zs = [v.co.z for v in f.verts]
    if not (min(zs) < ZL - 0.001 and max(zs) > ZL + 0.001):
        continue
    c = f.calc_center_median()
    if math.hypot(c.x, c.y) > 43: continue
    ids.add(f.index)
print("spanning faces", len(ids))
for i in sorted(ids)[:40]:
    f = bm.faces[i]
    c = f.calc_center_median()
    vs = " ".join("(%.2f,%.2f,%.3f)" % (v.co.x, v.co.y, v.co.z) for v in f.verts)
    print("  c=(%.2f,%.2f,%.3f) n=(%.2f,%.2f,%.2f) %s" % (c.x, c.y, c.z, f.normal.x, f.normal.y, f.normal.z, vs))
bm.free()
