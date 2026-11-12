import bpy, bmesh, math, os
from mathutils import Vector
ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, r"blender\_work\rev4_stage.blend"))
body = bpy.data.objects['Enclosure_Body']
bm = bmesh.new(); bm.from_mesh(body.data); bm.transform(body.matrix_world)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table(); bm.edges.ensure_lookup_table()

def zone(v, cx=30.0, cy=-55.0):
    dx, dy = v.co.x - cx, v.co.y - cy
    r = math.hypot(dx, dy)
    th = math.degrees(math.atan2(-dy, dx))
    return r, th

for zq in (54.34, 54.35, 54.36, 54.50, 54.55, 54.56):
    vs = [v for v in bm.verts if abs(v.co.z - zq) < 0.005]
    zs = [v for v in vs if -20 < zone(v)[1] < 70]
    print(f'z={zq:.3f} allverts={len(vs)} corner={len(zs)}')
    if zs:
        rs = [zone(v)[0] for v in zs]
        print('   r range', round(min(rs), 3), round(max(rs), 3))

print('--- dihedral angles of edges in FR shoulder region ---')
rows = []
for e in bm.edges:
    if len(e.link_faces) != 2: continue
    a, b = e.verts
    r1, th1 = zone(a); r2, th2 = zone(b)
    z1, z2 = a.co.z, b.co.z
    if not (49.0 <= min(z1, z2) and max(z1, z2) <= 55.0): continue
    if not (r1 < 14 and r2 < 14): continue
    if not (-18 < th1 < 70 and -18 < th2 < 70): continue
    if e.link_faces[0].normal.length < 1e-9 or e.link_faces[1].normal.length < 1e-9: continue
    ang = math.degrees(e.link_faces[0].normal.angle(e.link_faces[1].normal))
    rows.append((ang, z1, z2, th1, th2, r1, r2))
rows.sort(reverse=True)
print('edges in zone', len(rows))
for r in rows[:15]:
    print('  ang %5.2f z %.2f-%.2f th %.1f-%.1f r %.2f-%.2f' % r)

print('--- edges at seam heights (FR) ---')
for zq in (54.35, 54.55):
    es = []
    for e in bm.edges:
        if len(e.link_faces) != 2: continue
        a, b = e.verts
        if abs(a.co.z - zq) < 0.02 and abs(b.co.z - zq) < 0.02:
            r, th = zone(a)
            if -20 < th < 70 and r < 14:
                if e.link_faces[0].normal.length < 1e-9 or e.link_faces[1].normal.length < 1e-9: continue
                ang = math.degrees(e.link_faces[0].normal.angle(e.link_faces[1].normal))
                es.append((ang, th, r, b.co.x - a.co.x, b.co.y - a.co.y, b.co.z - a.co.z))
    es.sort(reverse=True)
    print(f'z{zq} edges {len(es)}  top angles:')
    for s in es[:8]:
        print('   ang %5.2f th %6.1f r %6.3f d(%.3f,%.3f,%.3f)' % s)
bm.free()
print('DONE')
