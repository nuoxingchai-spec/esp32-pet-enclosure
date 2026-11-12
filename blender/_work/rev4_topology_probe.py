import bpy, bmesh, math
from mathutils import Vector

P = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev4_stage3.blend"
bpy.ops.wm.open_mainfile(filepath=P)

body = None
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith('Enclosure_Body'):
        body = o
print("BODY", body.name, len(body.data.vertices), len(body.data.polygons))
mw = body.matrix_world
print("MW", [round(v, 4) for v in mw.translation])

me = body.data
bm = bmesh.new(); bm.from_mesh(me)
bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
zseam = 54.35 - mw.translation.z

def sec(y0, tag):
    print("=== SECTION y=%s (%s) ===" % (y0, tag))
    rows = []
    for v in bm.verts:
        if abs(v.co.y - y0) < 0.45 and v.co.x > 34.0 and 38.5 < v.co.z < 44.5:
            rows.append((round(v.co.z, 4), round(v.co.x, 4), len(v.link_faces), len(v.link_edges)))
    rows.sort()
    for r in rows:
        print("  z=%8.4f x=%9.4f f=%d e=%d" % r)
    # outer faces in band
    print("  -- outer faces (normal +x dominant) --")
    frows = []
    for f in bm.faces:
        c = f.calc_center_median()
        if abs(c.y - y0) < 0.45 and c.x > 34.0 and 38.5 < c.z < 44.5 and f.normal.x > 0.7:
            frows.append((round(c.z, 4), round(c.x, 4), round(math.degrees(f.normal.angle(Vector((1,0,0)))), 2), round(f.calc_area(), 6)))
    frows.sort()
    for r in frows:
        print("  face z=%8.4f x=%9.4f tilt=%6.2f area=%0.6f" % r)

sec(0.0, "+X wall center")
sec(-30.0, "+X hip")
sec(-45.0, "+X hip rear")

# crease audit around seam
print("=== CREASE AUDIT (edges near seam, outer) ===")
bnd = 0
for e in bm.edges:
    if len(e.link_faces) != 2:
        continue
    a, b = e.verts
    zm = (a.co.z + b.co.z) * 0.5
    if abs(zm - zseam) > 1.4:
        continue
    c = (a.co + b.co) * 0.5
    if c.x < 34.0 or abs(c.y) > 57.0:
        continue
    n1, n2 = e.link_faces[0].normal, e.link_faces[1].normal
    if n1.length < 1e-9 or n2.length < 1e-9:
        ang = -1
    else:
        ang = math.degrees(n1.angle(n2))
    if ang > 2.0:
        print("  edge z=%7.4f y=%8.3f x=%8.3f ang=%6.2f len=%7.4f" % (zm, c.y, c.x, ang, e.calc_length()))

# count sharp flagged edges
sharp = sum(1 for e in me.edges if e.use_edge_sharp)
print("SHARP_FLAGS", sharp)
bm.free()
