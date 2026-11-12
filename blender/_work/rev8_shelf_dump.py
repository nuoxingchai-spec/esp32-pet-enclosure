import bpy, math, json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev6_corner.blend")
ob = bpy.data.objects["Enclosure_Body"]
me = ob.data
SEAM = 40.35
edge_faces = {}
for p in me.polygons:
    for ek in p.edge_keys:
        edge_faces.setdefault(ek, []).append(p.index)
horiz = [p for p in me.polygons if abs(p.center.z - SEAM) < 0.03 and p.normal.z > 0.9]
outer = []
for p in horiz:
    cxy = Vector((p.center.x, p.center.y)); cn = cxy.normalized()
    out = inn = 0
    for ek in p.edge_keys:
        for fi in edge_faces.get(ek, []):
            if fi == p.index: continue
            f = me.polygons[fi]
            if abs(f.normal.z) > 0.3: continue
            n = Vector((f.normal.x, f.normal.y))
            if n.length < 1e-6: continue
            d = n.normalized().dot(cn)
            if d > 0.25: out += 1
            elif d < -0.25: inn += 1
    if inn == 0 and out > 0: outer.append(p.index)
lines = []
lines.append("FACE COUNT %d" % len(outer))
for fi in sorted(outer):
    p = me.polygons[fi]
    lines.append("F%d area=%.6f n=(%.3f,%.3f,%.3f)" % (fi, p.area, p.normal.x, p.normal.y, p.normal.z))
    for v in p.vertices:
        co = me.vertices[v].co
        lines.append("   v%d (%.4f, %.4f, %.4f) vr=%.4f" % (v, co.x, co.y, co.z, math.hypot(co.x, co.y)))
# duplicate positions among shelf verts
shelf_v = {}
for fi in outer:
    for v in me.polygons[fi].vertices:
        co = me.vertices[v].co
        shelf_v[v] = co
from collections import defaultdict
bypos = defaultdict(list)
for v, co in shelf_v.items():
    bypos[(round(co.x, 3), round(co.y, 3), round(co.z, 3))].append(v)
lines.append("DUP POSITIONS:")
for k, vs in bypos.items():
    if len(vs) > 1:
        lines.append("  %s -> %s" % (k, vs))
# vert -> faces for a few sample verts incl duplicates
vf = defaultdict(list)
for p in me.polygons:
    for v in p.vertices: vf[v].append(p.index)
lines.append("SAMPLE DUP VERTS:")
for k, vs in list(bypos.items())[:6]:
    for v in vs:
        fs = vf[v]
        lines.append("  v%d faces=%s" % (v, [(f, me.polygons[f].index, tuple(round(c, 2) for c in me.polygons[f].normal), round(me.polygons[f].area, 4)) for f in fs]))
open(r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev8_shelf_dump.txt", "w", encoding="utf-8").write("\n".join(lines))
print("written", len(lines), "lines")
