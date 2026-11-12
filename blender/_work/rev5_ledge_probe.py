import bpy, bmesh, math
from mathutils import Vector

P = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=P)
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world
ZL = 54.35 - mw.translation.z
me = body.data
bm = bmesh.new(); bm.from_mesh(me)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()

print("rows at +X y=-50")
for v in sorted((v for v in bm.verts if abs(v.co.y + 50) < 0.4 and v.co.x > 37.5 and 39.0 < v.co.z < 41.2), key=lambda v: v.co.z):
    print("  z=%.4f x=%.4f" % (v.co.z, v.co.x))

print("--- faces touching z=ZL band, +X wall ---")
n = 0
for f in bm.faces:
    c = f.calc_center_median()
    if abs(c.y + 50) < 0.6 and c.x > 37.8 and abs(c.z - ZL) < 0.08:
        n += 1
        print("  z=%.4f x=%.4f nz=%.2f area=%.6f verts=%d" % (c.z, c.x, f.normal.z, f.calc_area(), len(f.verts)))
print("count near wall", n)

# ledge candidates: mostly horizontal, thin, within band
cands = []
for f in bm.faces:
    zs = [v.co.z for v in f.verts]
    if min(zs) < ZL - 0.02 or max(zs) > ZL + 0.02:
        continue
    if abs(f.normal.z) < 0.7:
        continue
    cands.append(f)
print("ledge cands", len(cands), "area sum", round(sum(f.calc_area() for f in cands), 4))
if cands:
    rs = []
    for f in cands:
        c = f.calc_center_median()
        rs.append(math.hypot(c.x, c.y))
    print("ledge radial range", round(min(rs), 3), round(max(rs), 3))
    zs = [v.co.z for f in cands for v in f.verts]
    print("ledge z range", round(min(zs), 5), round(max(zs), 5))
    # per-quad ring pair info
    outer = set(); inner = set()
    for f in cands:
        rv = []
        for v in f.verts:
            rv.append((math.hypot(v.co.x, v.co.y), v))
        rv.sort()
        inner.add(rv[0][1]); inner.add(rv[1][1])
        outer.add(rv[-1][1]); outer.add(rv[-2][1])
    print("outer verts", len(outer), "inner verts", len(inner), "shared", len(outer & inner))
    zs_o = sorted(round(v.co.z, 4) for v in outer)
    zs_i = sorted(round(v.co.z, 4) for v in inner)
    print("outer z sample", zs_o[:6], "...", zs_o[-6:])
    print("inner z sample", zs_i[:6], "...", zs_i[-6:])

# all faces z-bands count
from collections import Counter
cnt = Counter(round(v.co.z, 3) for v in bm.verts if 39.9 < v.co.z < 41.1)
print("z histogram 39.9-41.1 (top 25):", sorted(cnt.items())[:25])
bm.free()
