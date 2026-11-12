import bpy, bmesh, math
from mathutils import Vector

P = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=P)
body = bpy.data.objects['Enclosure_Body']
bm = bmesh.new(); bm.from_mesh(body.data)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
ZL = 40.35

# edge at x~38.977, z=40.35, y~-50.57
tgt = None
for e in bm.edges:
    a, b = e.verts
    if abs(a.co.z - ZL) < 0.002 and abs(b.co.z - ZL) < 0.002:
        xm = (a.co.x + b.co.x) / 2; ym = (a.co.y + b.co.y) / 2
        if 38.95 < xm < 39.0 and -52 < ym < -49:
            tgt = e; break
print("TARGET EDGE", tgt)
if tgt:
    for v in tgt.verts:
        print("  vert idx=%d co=(%.4f,%.4f,%.4f)" % (v.index, v.co.x, v.co.y, v.co.z))
    for f in tgt.link_faces:
        c = f.calc_center_median()
        vs = " ".join("[%d](%.3f,%.3f,%.3f)" % (v.index, v.co.x, v.co.y, v.co.z) for v in f.verts)
        print("  face idx=%d c=(%.2f,%.2f,%.3f) n=(%.2f,%.2f,%.2f) verts=%d" %
              (f.index, c.x, c.y, c.z, f.normal.x, f.normal.y, f.normal.z, len(f.verts)))
        print("      " + vs)

print("--- z=40.35 verts on outer wall (r 38.8..39.1) ---")
for v in sorted((v for v in bm.verts if abs(v.co.z - ZL) < 0.002 and 38.5 < math.hypot(v.co.x, v.co.y) < 39.3),
                key=lambda v: math.atan2(v.co.y, v.co.x)):
    print("  [%d] (%.4f,%.4f,%.4f) r=%.4f" % (v.index, v.co.x, v.co.y, v.co.z, math.hypot(v.co.x, v.co.y)))
print("--- horizontal faces z=40.35, any radius, nz>0.7, listing outer xy ---")
cnt = 0
for f in bm.faces:
    zs = [v.co.z for v in f.verts]
    if max(abs(z - ZL) for z in zs) > 0.002 or abs(f.normal.z) < 0.7: continue
    cnt += 1
    if cnt <= 60:
        xs = [v.co.x for v in f.verts]; ys = [v.co.y for v in f.verts]
        c = f.calc_center_median()
        print("  f[%d] c=(%.2f,%.2f,%.3f) x[%.3f,%.3f] y[%.3f,%.3f] a=%.4f nv=%d" %
              (f.index, c.x, c.y, c.z, min(xs), max(xs), min(ys), max(ys), f.calc_area(), len(f.verts)))
print("total horizontal at seam", cnt)
bm.free()
