import bpy, bmesh, math, os
from mathutils import Vector

ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
F = os.path.join(ROOT, r"blender\robot_dog_enclosure_v3.blend")
OUT = os.path.join(ROOT, r"blender\_work")

bpy.ops.wm.open_mainfile(filepath=F)
sc = bpy.context.scene
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world
mi = mw.inverted()
M3 = mw.to_3x3()
M3i = M3.inverted()
dg = bpy.context.evaluated_depsgraph_get()

def audit(ob, tag):
    bm = bmesh.new(); bm.from_mesh(ob.data)
    nm = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    bnd = sum(1 for e in bm.edges if len(e.link_faces) < 2)
    zero = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    bm.verts.ensure_lookup_table()
    par = list(range(len(bm.verts)))
    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for e in bm.edges:
        a, b = find(e.verts[0].index), find(e.verts[1].index)
        if a != b: par[a] = b
    comps = len({find(i) for i in range(len(bm.verts))})
    vol = bm.calc_volume(signed=True)
    zs = [v.co.z for v in bm.verts]
    print(f"AUDIT {tag:8s} v={len(bm.verts):6d} f={len(bm.faces):6d} nm={nm} bnd={bnd} zero={zero} comps={comps} vol={vol:.1f} localz[{min(zs):.2f},{max(zs):.2f}]")
    bm.free()
    return nm, bnd, zero, comps

print("=== BEFORE ===")
audit(body, 'BODY')

# ---------------------------------------------------------------- cutter
CORNERS = [('FR', 30.0, -55.0, 1, -1), ('FL', -30.0, -55.0, -1, -1),
           ('RR', 30.0, 55.0, 1, 1),  ('RL', -30.0, 55.0, -1, 1)]
THS = [-15 + i for i in range(81)]            # -15..65, 1 deg
ZS = [49.0 + 0.35 * i for i in range(16)]     # 49.00..54.25
ZS += [54.30, 54.34, 54.35, 54.36, 54.50, 55.0, 56.0, 57.0, 58.0, 59.0, 60.0]
R_OUT = 42.0

def smooth(t):
    t = max(0.0, min(1.0, t)); return t * t * (3.0 - 2.0 * t)

def clear(th):
    if th < 0.0:
        return 0.12 * smooth(-th / 15.0)
    if th > 44.5:
        return 0.12 * smooth((th - 44.5) / 20.5)
    return 0.0

def ray_r(cx, cy, sx, sy, z, th_deg, back=60.0):
    a = math.radians(th_deg)
    ux, uy = sx * math.cos(a), sy * math.sin(a)
    org = mi @ Vector((cx + back * ux, cy + back * uy, z))
    d = (M3i @ Vector((-ux, -uy, 0.0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=300.0, depsgraph=dg)
    if not ok: return None
    p = mw @ loc
    return math.hypot(p.x - cx, p.y - cy)

bm = bmesh.new()
for tag, cx, cy, sx, sy in CORNERS:
    rl = {}; ru = {}
    for th in THS:
        rl[th] = ray_r(cx, cy, sx, sy, 52.0, th)
        ru[th] = ray_r(cx, cy, sx, sy, 56.0, th)
        if rl[th] is None or ru[th] is None:
            raise RuntimeError(f'miss {tag} {th}')
    rows = []
    for z in ZS:
        row = []
        for th in THS:
            if z <= 54.35:
                s = smooth((z - 49.0) / 5.35)
                r = rl[th] + s * (ru[th] - rl[th]) + clear(th)
            else:
                r = ru[th] + 0.12
            a = math.radians(th)
            row.append((cx + sx * r * math.cos(a), cy + sy * r * math.sin(a), z))
        rows.append(row)
    V_in = [[bm.verts.new(p) for p in row] for row in rows]
    V_out = [[bm.verts.new((cx + sx * R_OUT * math.cos(math.radians(th)),
                            cy + sy * R_OUT * math.sin(math.radians(th)), z)) for th in THS] for z in ZS]
    NI, NJ = len(THS), len(ZS)
    for j in range(NJ - 1):
        for i in range(NI - 1):
            bm.faces.new((V_in[j][i], V_in[j][i + 1], V_in[j + 1][i + 1], V_in[j + 1][i]))
            bm.faces.new((V_out[j][i], V_out[j + 1][i], V_out[j + 1][i + 1], V_out[j][i + 1]))
    for i in range(NI - 1):
        bm.faces.new((V_in[0][i], V_out[0][i], V_out[0][i + 1], V_in[0][i + 1]))
        bm.faces.new((V_in[NJ - 1][i], V_in[NJ - 1][i + 1], V_out[NJ - 1][i + 1], V_out[NJ - 1][i]))
    for j in range(NJ - 1):
        bm.faces.new((V_in[j][0], V_in[j + 1][0], V_out[j + 1][0], V_out[j][0]))
        bm.faces.new((V_in[j][NI - 1], V_out[j][NI - 1], V_out[j + 1][NI - 1], V_in[j + 1][NI - 1]))

bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
nm_c = sum(1 for e in bm.edges if len(e.link_faces) != 2)
print('CUTTER v', len(bm.verts), 'f', len(bm.faces), 'nm', nm_c, 'vol', round(bm.calc_volume(signed=True), 1))
cut_me = bpy.data.meshes.new('Shoulder_Cutter')
bm.to_mesh(cut_me); bm.free()
cut = bpy.data.objects.new('Shoulder_Cutter', cut_me)
sc.collection.objects.link(cut)
cut.hide_render = True

# ---------------------------------------------------------------- boolean
bpy.context.view_layer.objects.active = body
for o in sc.objects: o.select_set(False)
body.select_set(True)
mod = body.modifiers.new('shoulder', 'BOOLEAN')
mod.operation = 'DIFFERENCE'; mod.solver = 'MANIFOLD'; mod.object = cut
try:
    bpy.ops.object.modifier_apply(modifier=mod.name)
    print('APPLIED manifold')
except Exception as e:
    print('MANIFOLD failed:', e)
    body.modifiers.clear()
    mod = body.modifiers.new('shoulder', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'; mod.solver = 'EXACT'; mod.object = cut
    bpy.ops.object.modifier_apply(modifier=mod.name)
    print('APPLIED exact')
cut.hide_viewport = True
print("=== AFTER CUT ===")
audit(body, 'CUT')

# profile after cut
dg2 = bpy.context.evaluated_depsgraph_get()
def ray_body(z, th_deg, cx=30.0, cy=-55.0, sx=1, sy=-1):
    a = math.radians(th_deg)
    ux, uy = sx * math.cos(a), sy * math.sin(a)
    org = mi @ Vector((cx + 60 * ux, cy + 60 * uy, z))
    d = (M3i @ Vector((-ux, -uy, 0.0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=300.0, depsgraph=dg2)
    if not ok: return None
    p = mw @ loc
    return math.hypot(p.x - cx, p.y - cy)
print('post-cut FR r(theta)')
for z in (50.0, 52.0, 54.30, 54.34, 54.35, 54.4, 55.0, 56.0):
    row = []
    for th in (-12, 0, 10, 20, 30, 35, 40, 44, 46, 50, 60):
        r = ray_body(z, th)
        row.append('  --  ' if r is None else f'{r:6.3f}')
    print(f'z{z:6.2f} ' + ' '.join(row))
print('cols    -12     0    10    20    30    35    40    44    46    50    60')

# ---------------------------------------------------------------- seam lift (local coords)
ZSEAM_L = 54.35 - mw.translation.z
H = 0.20
bmd = bmesh.new(); bmd.from_mesh(body.data)
bmd.verts.ensure_lookup_table(); bmd.faces.ensure_lookup_table()

def is_sliver(f):
    zs = [v.co.z for v in f.verts]
    return min(zs) > ZSEAM_L - 0.05 and max(zs) < ZSEAM_L + 0.05 and f.normal.z > 0.9

ups = []
for v in bmd.verts:
    if abs(v.co.z - ZSEAM_L) > 0.02:
        continue
    above = any((not is_sliver(f)) and max(x.co.z for x in f.verts) > ZSEAM_L + 0.05 for f in v.link_faces)
    below = any((not is_sliver(f)) and min(x.co.z for x in f.verts) < ZSEAM_L - 0.05 for f in v.link_faces)
    if above and not below:
        ups.append(v)
print('UP verts', len(ups))

targets = []
miss = 0
for v in ups:
    d = Vector((v.co.x, v.co.y, 0.0))
    if d.length < 1e-6:
        miss += 1; continue
    d.normalize()
    org = Vector((v.co.x + 12.0 * d.x, v.co.y + 12.0 * d.y, ZSEAM_L - 0.01))
    ok, loc, nor, idx = body.ray_cast(org, (-d).normalized(), distance=40.0, depsgraph=dg2)
    if not ok:
        miss += 1; continue
    targets.append((v, loc.copy()))
for v, loc in targets:
    v.co.x = loc.x; v.co.y = loc.y; v.co.z = ZSEAM_L + H
print('moved', len(targets), 'miss', miss)

bmd.normal_update()
fan = 0; bad = 0
for f in bmd.faces:
    zs = [v.co.z for v in f.verts]
    if min(zs) > ZSEAM_L - 0.01 and max(zs) < ZSEAM_L + H + 0.01:
        c = f.calc_center_median()
        r = Vector((c.x, c.y, 0.0))
        if r.length > 1e-6 and f.normal.dot(r.normalized()) < -0.2:
            bad += 1
        fan += 1
print('fan faces', fan, 'inward normals', bad)
bmesh.ops.recalc_face_normals(bmd, faces=bmd.faces[:])
bmd.to_mesh(body.data); bmd.free(); body.data.update()

print("=== AFTER LIFT ===")
res = audit(body, 'LIFT')
print('dims', tuple(round(v, 3) for v in body.dimensions))
b = [mw @ Vector(c) for c in body.bound_box]
print('bbox x', round(min(p.x for p in b), 3), round(max(p.x for p in b), 3),
      'y', round(min(p.y for p in b), 3), round(max(p.y for p in b), 3),
      'z', round(min(p.z for p in b), 3), round(max(p.z for p in b), 3))

# ---------------------------------------------------------------- render body-only
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading
sh.light = 'STUDIO'; sh.studio_light = 'Default'; sh.color_type = 'OBJECT'
sh.show_cavity = True; sh.cavity_type = 'BOTH'
sh.curvature_ridge_factor = 2.0; sh.curvature_valley_factor = 2.0
sh.show_shadows = True; sh.shadow_intensity = 0.35
sc.world.color = (0.82, 0.85, 0.9)
sc.render.resolution_x = 1200; sc.render.resolution_y = 900
sc.render.image_settings.file_format = 'PNG'

hidden = []
for o in sc.objects:
    if o.type == 'MESH' and o.name != 'Enclosure_Body' and not o.hide_render:
        o.hide_render = True; hidden.append(o)
cam_d = bpy.data.cameras.new('Rev4Cam')
cam = bpy.data.objects.new('Rev4Cam', cam_d)
sc.collection.objects.link(cam)
sc.camera = cam
cam_d.lens = 80

def look(pos, tgt, lens=80):
    cam.location = pos; cam.data.lens = lens
    d = Vector(tgt) - Vector(pos)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

VIEWS = [
    ('q_fr', (150, -120, 80), (36, -58, 47), 80),
    ('q_rl', (-150, 120, 80), (-36, 58, 47), 80),
    ('side', (170, -62, 50), (39, -58, 50), 75),
    ('top', (70, -96, 132), (0, -4, 52), 70),
    ('q_fl', (-150, -120, 80), (-36, -58, 47), 80),
    ('q_rr', (150, 120, 80), (36, 58, 47), 80),
]
for tag, pos, tgt, lens in VIEWS:
    look(pos, tgt, lens)
    sc.render.filepath = os.path.join(OUT, f'r4_{tag}.png')
    bpy.ops.render.render(write_still=True)

for o in hidden:
    o.hide_render = False
bpy.data.objects.remove(cam, do_unlink=True)
bpy.data.cameras.remove(cam_d)
cut.hide_viewport = False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'rev4_stage.blend'))
print('DONE')
