import bpy, math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev6_corner.blend")
ob = bpy.data.objects["Enclosure_Body"]
me = ob.data
SEAM = 40.35
vert_faces = {}
for p in me.polygons:
    for v in p.vertices:
        vert_faces.setdefault(v, []).append(p.index)
ann_idx = {p.index for p in me.polygons if p.normal.z > 0.9 and abs(p.center.z - SEAM) < 0.03}
def is_collar(v):
    for f in vert_faces[v]:
        if f in ann_idx:
            continue
        p = me.polygons[f]
        if all(me.vertices[q].co.z >= SEAM - 0.005 for q in p.vertices):
            return True
    return False
pat = {}
inner = set()
for fi in sorted(ann_idx):
    p = me.polygons[fi]
    tags = tuple(is_collar(v) for v in p.vertices)
    pat[tags] = pat.get(tags, 0) + 1
    for v, t in zip(p.vertices, tags):
        if t:
            inner.add(v)
print("patterns (collar tag per vert):", pat)
print("inner verts:", len(inner))
for v in sorted(inner):
    co = me.vertices[v].co
    ns = [me.polygons[f].normal for f in vert_faces[v] if f not in ann_idx and abs(me.polygons[f].normal.z) < 0.3]
    nm = sum(ns, Vector()) / max(1, len(ns))
    print("  v%d co=(%.3f, %.3f, %.3f) radius=%.3f n=(%.2f, %.2f) faces=%d" % (v, co.x, co.y, co.z, math.hypot(co.x, co.y), nm.x, nm.y, len(vert_faces[v])))
# annulus face vert patterns sample
for fi in sorted(ann_idx)[:12]:
    p = me.polygons[fi]
    print(fi, [(v, tuple(round(c, 2) for c in me.vertices[v].co), is_collar(v)) for v in p.vertices])
