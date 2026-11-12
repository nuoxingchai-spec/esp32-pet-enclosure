import bpy, bmesh, math
from mathutils import Vector

P = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=P)
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world
bm = bmesh.new(); bm.from_mesh(body.data)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
print("verts |y+50|<3.5, x>37, 39.4<z<41.1")
rows = []
for v in bm.verts:
    if abs(v.co.y + 50) < 3.5 and v.co.x > 37.0 and 39.4 < v.co.z < 41.1:
        rows.append((round(v.co.z, 4), round(v.co.y, 3), round(v.co.x, 4), len(v.link_faces)))
for r in sorted(rows):
    print("  z=%.4f y=%8.3f x=%9.4f f=%d" % r)

print("--- faces with any vert in window ---")
seen = set()
for v in bm.verts:
    if abs(v.co.y + 50) < 3.5 and v.co.x > 37.0 and 39.4 < v.co.z < 41.1:
        for f in v.link_faces:
            if f.index in seen: continue
            seen.add(f.index)
            c = f.calc_center_median()
            vs = " ".join("(%.2f,%.2f,%.3f)" % (x.co.x, x.co.y, x.co.z) for x in f.verts)
            print("  c=(%.2f,%.2f,%.3f) n=(%.2f,%.2f,%.2f) a=%.5f %s" %
                  (c.x, c.y, c.z, f.normal.x, f.normal.y, f.normal.z, f.calc_area(), vs))

# edges spanning the seam with high dihedral
print("--- crease edges z 39.8-41.0, x>37.3, |y+50|<4 ---")
for e in bm.edges:
    if len(e.link_faces) != 2: continue
    a, b = e.verts
    zm = (a.co.z + b.co.z) / 2
    ym = (a.co.y + b.co.y) / 2
    xm = (a.co.x + b.co.x) / 2
    if not (39.8 < zm < 41.0 and xm > 37.3 and abs(ym + 50) < 4): continue
    n1, n2 = e.link_faces[0].normal, e.link_faces[1].normal
    if n1.length < 1e-9 or n2.length < 1e-9: continue
    ang = math.degrees(n1.angle(n2))
    if ang > 5:
        print("  e z=%.4f y=%8.3f x=%8.4f ang=%6.2f len=%.4f" % (zm, ym, xm, ang, e.calc_length()))
bm.free()
