import bpy, math
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
print("horizontal faces at seam:", len(horiz))
outer_faces, inner_faces = [], []
for p in horiz:
    cxy = Vector((p.center.x, p.center.y))
    cn = cxy.normalized() if cxy.length > 1e-6 else Vector((0, 0))
    out = inn = 0
    for ek in p.edge_keys:
        for fi in edge_faces.get(ek, []):
            if fi == p.index:
                continue
            f = me.polygons[fi]
            if abs(f.normal.z) > 0.3:
                continue
            n = Vector((f.normal.x, f.normal.y))
            if n.length < 1e-6:
                continue
            d = n.normalized().dot(cn)
            if d > 0.25:
                out += 1
            elif d < -0.25:
                inn += 1
    if inn == 0 and out > 0:
        outer_faces.append(p.index)
    else:
        inner_faces.append(p.index)
print("outer shelf faces:", len(outer_faces), "other horiz faces:", len(inner_faces))
print("outer face centers:", [(round(me.polygons[i].center.x, 1), round(me.polygons[i].center.y, 1)) for i in outer_faces[:30]])
# for outer shelf, find collar-ring verts (adjacent wall face entirely above)
vert_faces = {}
for p in me.polygons:
    for v in p.vertices:
        vert_faces.setdefault(v, []).append(p.index)
osset = set(outer_faces)
inner_v = set()
for fi in outer_faces:
    p = me.polygons[fi]
    for v in p.vertices:
        for g in vert_faces[v]:
            if g in osset:
                continue
            f = me.polygons[g]
            if abs(f.normal.z) < 0.3 and all(me.vertices[q].co.z >= SEAM - 0.005 for q in f.vertices):
                inner_v.add(v)
print("outer shelf collar-ring verts:", len(inner_v))
for v in sorted(inner_v):
    co = me.vertices[v].co
    print("  v%d co=(%.3f, %.3f) z=%.3f r=%.3f" % (v, co.x, co.y, co.z, math.hypot(co.x, co.y)))
# check outer-shelf verts all at z=40.35 and list their max radial extents
zs = [me.vertices[v].co.z for fi in outer_faces for v in me.polygons[fi].vertices]
print("outer shelf z range", round(min(zs), 4), round(max(zs), 4))
print("outer shelf vert count", len({v for fi in outer_faces for v in me.polygons[fi].vertices}))
