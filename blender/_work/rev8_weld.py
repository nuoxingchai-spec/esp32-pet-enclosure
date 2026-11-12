import bpy, bmesh, math, os
from mathutils import Vector

ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
OUT = os.path.join(ROOT, r"blender\_work")
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT, "rev6_corner.blend"))
sc = bpy.context.scene
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world; mi = mw.inverted()
M3i = mw.to_3x3().inverted()
dg = bpy.context.evaluated_depsgraph_get()
SEAM = 40.35
H = 0.15

def audit(tag):
    bm = bmesh.new(); bm.from_mesh(body.data)
    nm = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    bnd = sum(1 for e in bm.edges if len(e.link_faces) < 2)
    zero = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    vol = bm.calc_volume(signed=True)
    print(f"AUDIT {tag:8s} v={len(bm.verts):6d} f={len(bm.faces):6d} nm={nm} bnd={bnd} zero={zero} vol={vol:.1f}")
    bm.free()

audit('before')
me = body.data
edge_faces = {}
for p in me.polygons:
    for ek in p.edge_keys:
        edge_faces.setdefault(ek, []).append(p.index)
vert_faces = {}
for p in me.polygons:
    for v in p.vertices:
        vert_faces.setdefault(v, []).append(p.index)

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
    if inn == 0 and out > 0:
        outer.append(p.index)
osset = set(outer)
ring = set()
for fi in outer:
    for v in me.polygons[fi].vertices:
        for g in vert_faces[v]:
            f = me.polygons[g]
            if g in osset or abs(f.normal.z) > 0.3:
                continue
            if all(me.vertices[q].co.z >= SEAM - 0.005 for q in f.vertices):
                ring.add(v); break
print("outer shelf faces", len(outer), "ring verts", len(ring))

# group by position, outward normal from adjacent vertical faces (exclude shelf faces)
from collections import defaultdict
groups = defaultdict(list)
for v in ring:
    co = me.vertices[v].co
    groups[(round(co.x, 4), round(co.y, 4), round(co.z, 4))].append(v)
moves = []
skipped = []
for key, vs in groups.items():
    co = me.vertices[vs[0]].co.copy()
    ns = []
    for v in vs:
        for fi in vert_faces[v]:
            if fi in osset: continue
            f = me.polygons[fi]
            if abs(f.normal.z) > 0.3: continue
            nv = Vector((f.normal.x, f.normal.y))
            if nv.length > 1e-6: ns.append(nv.normalized())
    if not ns:
        skipped.append((key, 'no-normal')); continue
    n = sum(ns, Vector((0.0, 0.0))) / len(ns)
    if n.length < 1e-6:
        skipped.append((key, 'zero-normal')); continue
    n.normalize()
    org = mi @ Vector((co.x + n.x * 2.0, co.y + n.y * 2.0, SEAM - 0.05))
    d = (M3i @ Vector((-n.x, -n.y, 0.0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=4.0, depsgraph=dg)
    if not ok:
        skipped.append((key, 'miss')); continue
    hit = mw @ loc
    delta = (Vector((hit.x, hit.y)) - Vector((co.x, co.y))).dot(n)
    if not (-0.002 <= delta <= 0.09):
        skipped.append((key, 'delta=%.4f' % delta)); continue
    delta = max(0.0, delta)
    moves.append((vs, Vector((co.x, co.y, SEAM)), n, delta))
print("groups", len(groups), "moves", len(moves), "skipped", len(skipped))
print("skip detail", skipped[:12])
ds = sorted(m[3] for m in moves)
print("delta min/median/max %.4f %.4f %.4f" % (ds[0], ds[len(ds)//2], ds[-1]))
import collections
print("delta hist 0.005 bins", sorted(collections.Counter(int(d / 0.005) * 0.005 for d in ds).items()))

for vs, co, n, delta in moves:
    for v in vs:
        me.vertices[v].co.x += n.x * delta
        me.vertices[v].co.y += n.y * delta
        me.vertices[v].co.z = SEAM + H
me.update()
body.data.update()
audit('AFTER')

# profile check across seam after move (world z; local = world-14)
for y in (-30, -45, -50, 0, 30):
    got = []
    for wz in (54.28, 54.32, 54.38, 54.42, 54.50):
        org = mi @ Vector((60, y, wz))
        d = (M3i @ Vector((-1, 0, 0))).normalized()
        ok, loc, nor, idx = body.ray_cast(org, d, distance=60, depsgraph=dg)
        got.append(round((mw @ loc).x, 4) if ok else None)
    print("profile y=%d" % y, got)

print('smooth polys', sum(1 for p in body.data.polygons if p.use_smooth), 'of', len(body.data.polygons))

# render
sh = sc.display.shading
sh.light = 'STUDIO'; sh.studio_light = 'Default'; sh.color_type = 'OBJECT'
sh.show_cavity = True; sh.cavity_type = 'BOTH'
sh.curvature_ridge_factor = 2.0; sh.curvature_valley_factor = 2.0
sh.show_shadows = True; sh.shadow_intensity = 0.35
sc.world.color = (0.82, 0.85, 0.9)
sc.render.resolution_x = 1200; sc.render.resolution_y = 900
sc.render.image_settings.file_format = 'PNG'
for o in sc.objects:
    if o.type == 'MESH' and o.name != 'Enclosure_Body':
        o.hide_render = True; o.hide_viewport = True
cam = bpy.data.objects.get('C')
cam_d = None
if cam is None:
    cam_d = bpy.data.cameras.new('C'); cam = bpy.data.objects.new('C', cam_d)
    sc.collection.objects.link(cam)
sc.camera = cam
def look(pos, tgt, lens):
    cam.location = pos; cam.data.lens = lens
    d = Vector(tgt) - Vector(pos)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
VIEWS = [
    ('q', (150, -120, 80), (36, -58, 47), 80),
    ('sh', (120, -95, 66), (36.5, -59.0, 52.0), 135),
    ('seam', (120, -60, 57.4), (39.0, -50.0, 54.35), 150),
    ('mid', (100, -30, 58), (39, -25, 54.2), 130),
    ('front', (0, -135, 55.2), (0, -64, 54.35), 150),
    ('seam2', (90, -20, 62), (39.0, -40.0, 54.35), 120),
]
for tag, pos, tgt, lens in VIEWS:
    look(pos, tgt, lens)
    sc.render.filepath = os.path.join(OUT, f'r8_weld_{tag}.png')
    bpy.ops.render.render(write_still=True)
cut = bpy.data.objects.get('Shoulder_Cutter')
if cut: cut.hide_viewport = False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'rev8_weld.blend'))
print('DONE')
