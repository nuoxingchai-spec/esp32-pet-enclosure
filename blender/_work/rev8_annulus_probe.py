import bpy, math
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev6_corner.blend")
ob = bpy.data.objects["Enclosure_Body"]
me = ob.data
print("body verts %d polys %d" % (len(me.vertices), len(me.polygons)))
SEAM = 40.35

edge_faces = {}
for p in me.polygons:
    for ek in p.edge_keys:
        edge_faces.setdefault(ek, []).append(p.index)
vert_faces = {}
for p in me.polygons:
    for v in p.vertices:
        vert_faces.setdefault(v, []).append(p.index)

ann = [p for p in me.polygons if p.normal.z > 0.9 and abs(p.center.z - SEAM) < 0.03]
print("annulus faces:", len(ann))
if ann:
    zs = [me.vertices[v].co.z for p in ann for v in p.vertices]
    print("ann z range %.4f %.4f" % (min(zs), max(zs)))
    angs = sorted(math.degrees(math.atan2(p.center.y, p.center.x)) for p in ann)
    print("annulus angular extent", round(angs[0], 2), round(angs[-1], 2))
    gaps = [(round(a, 1), round(b, 1)) for a, b in zip(angs, angs[1:]) if b - a > 1.5]
    print("angular gaps >1.5deg:", gaps)
    # also angular histogram in 10 deg bins to see coverage
    import collections
    hist = collections.Counter(int(math.degrees(math.atan2(p.center.y, p.center.x)) // 10) * 10 for p in ann)
    print("hist", sorted(hist.items()))
    lens = []
    for p in ann:
        vs = [me.vertices[v].co for v in p.vertices]
        e = [(vs[i] - vs[(i + 1) % 3]).length for i in range(3)]
        lens.append((min(e), max(e)))
    print("ann edge len min/max overall: %.4f %.4f" % (min(x[0] for x in lens), max(x[1] for x in lens)))
    abovewall = belowwall = both = neither = 0
    inner_verts = []
    outer_verts = []
    for p in ann:
        for v in p.vertices:
            above = [f for f in vert_faces[v] if f != p.index and all(me.vertices[q].co.z >= SEAM - 0.005 for q in me.polygons[f].vertices)]
            below = [f for f in vert_faces[v] if f != p.index and all(me.vertices[q].co.z <= SEAM + 0.005 for q in me.polygons[f].vertices)]
            if above and below: both += 1
            elif above: abovewall += 1; inner_verts.append(v)
            elif below: belowwall += 1; outer_verts.append(v)
            else: neither += 1
    print("vert incidences above %d below %d both %d neither %d" % (abovewall, belowwall, both, neither))
    print("unique collar ring verts", len(set(inner_verts)), "lower edge verts", len(set(outer_verts)))
    print("sample inner", [tuple(round(c, 3) for c in me.vertices[v].co) for v in list(set(inner_verts))[:8]])
    print("sample outer", [tuple(round(c, 3) for c in me.vertices[v].co) for v in list(set(outer_verts))[:8]])
    # edge classification on a sample
    classify = {"above": 0, "below": 0, "other": 0}
    for p in ann[:600]:
        for ek in p.edge_keys:
            fs = [f for f in edge_faces.get(ek, []) if f != p.index]
            if not fs:
                classify["other"] += 1
                continue
            f = me.polygons[fs[0]]
            fz = [me.vertices[v].co.z for v in f.vertices]
            if min(fz) >= SEAM - 0.005:
                classify["above"] += 1
            elif max(fz) <= SEAM + 0.005:
                classify["below"] += 1
            else:
                classify["other"] += 1
    print("edge adjacency", classify)
    # wall faces crossing seam (span both sides)
    cross = [p for p in me.polygons if min(me.vertices[v].co.z for v in p.vertices) < SEAM - 0.005 and max(me.vertices[v].co.z for v in p.vertices) > SEAM + 0.005]
    print("faces crossing seam:", len(cross))
    if cross[:5]:
        for p in cross[:5]:
            print("  cross face", p.index, "n", tuple(round(c, 3) for c in p.normal), "z", round(min(me.vertices[v].co.z for v in p.vertices), 3), round(max(me.vertices[v].co.z for v in p.vertices), 3))
