import bpy, bmesh, math, os
from mathutils import Vector

ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
OUT = os.path.join(ROOT, r"blender\_work")
F = os.path.join(ROOT, r"blender\robot_dog_enclosure_v3.blend")

bpy.ops.wm.open_mainfile(filepath=F)
sc = bpy.context.scene
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world; mi = mw.inverted()
M3 = mw.to_3x3(); M3i = M3.inverted()
dg = bpy.context.evaluated_depsgraph_get()

def audit(tag):
    bm = bmesh.new(); bm.from_mesh(body.data)
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

print("=== CLEAN BASE ===")
audit('BODY')

def smooth(t):
    t = max(0.0, min(1.0, t)); return t * t * (3.0 - 2.0 * t)

def apply_boolean(obj, cutter, tag):
    bpy.context.view_layer.objects.active = obj
    for o in sc.objects: o.select_set(False)
    obj.select_set(True)
    mod = obj.modifiers.new(tag, 'BOOLEAN')
    mod.operation = 'DIFFERENCE'; mod.solver = 'MANIFOLD'; mod.object = cutter
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
        print('APPLIED manifold', tag)
    except Exception as e:
        print('MANIFOLD failed:', e)
        obj.modifiers.clear()
        mod = obj.modifiers.new(tag, 'BOOLEAN')
        mod.operation = 'DIFFERENCE'; mod.solver = 'EXACT'; mod.object = cutter
        bpy.ops.object.modifier_apply(modifier=mod.name)
        print('APPLIED exact', tag)

# ================================================================ 1) corner fin blend
CORNERS = [('FR', 30.0, -55.0, 1, -1), ('FL', -30.0, -55.0, -1, -1),
           ('RR', 30.0, 55.0, 1, 1),  ('RL', -30.0, 55.0, -1, 1)]
THS = [-15 + i for i in range(81)]
ZS = [49.0 + 0.35 * i for i in range(16)] + [54.30, 54.34, 54.35, 54.36, 54.50, 55.0, 56.0, 57.0, 58.0, 59.0, 60.0]
R_OUT = 42.0

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
print('CUTTER corner v', len(bm.verts), 'f', len(bm.faces), 'nm',
      sum(1 for e in bm.edges if len(e.link_faces) != 2), 'vol', round(bm.calc_volume(signed=True), 1))
cut_me = bpy.data.meshes.new('Shoulder_Cutter')
bm.to_mesh(cut_me); bm.free()
cut = bpy.data.objects.new('Shoulder_Cutter', cut_me)
sc.collection.objects.link(cut)
cut.hide_render = True

apply_boolean(body, cut, 'shoulder')
cut.hide_viewport = True
print("=== AFTER CORNER CUT ===")
audit('CUT')
dg = bpy.context.evaluated_depsgraph_get()

# ================================================================ 2) full-perimeter seam taper
N = 720
ZSEAM = 54.35
Z0 = 53.30
ZS2 = [Z0 - 0.05, Z0] + [Z0 + 1.05 * i / 21.0 for i in range(1, 22)] + [54.36, 54.40, 54.45, 54.60]
ZHI = 54.45
R_OUT2 = 74.0

def ray_axis(th_deg, z, back=80.0):
    a = math.radians(th_deg)
    ux, uy = math.cos(a), math.sin(a)
    org = mi @ Vector((back * ux, back * uy, z))
    d = (M3i @ Vector((-ux, -uy, 0.0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=300.0, depsgraph=dg)
    if not ok: return None
    p = mw @ loc
    return math.hypot(p.x, p.y)

THS2 = [360.0 * i / N for i in range(N)]
rL = []; rU = []
badL = 0; badU = 0
for i, th in enumerate(THS2):
    a = ray_axis(th, Z0); b = ray_axis(th, ZHI)
    if a is None or a < 30.0 or a > 70.0:
        badL += 1; a = None
    if b is None or b < 30.0 or b > 70.0:
        badU += 1; b = None
    rL.append(a); rU.append(b)
print('seam scan badL', badL, 'badU', badU)

def fill(arr):
    ok = [i for i, v in enumerate(arr) if v is not None]
    if not ok:
        raise RuntimeError('no valid samples')
    for i, v in enumerate(arr):
        if v is not None: continue
        lo = max([j for j in ok if j < i], default=None)
        hi = min([j for j in ok if j > i], default=None)
        if lo is None:
            lo = ok[-1] - N
        if hi is None:
            hi = ok[0] + N
        a = arr[lo % N]; b = arr[hi % N]
        t = (i - lo) / (hi - lo)
        arr[i] = a + t * (b - a)
fill(rL); fill(rU)

DELTA = []
for i in range(N):
    d = rL[i] - rU[i]
    if d != d or d < 0.0 or d > 0.08:
        DELTA.append(None)
    else:
        DELTA.append(d)
nd = sum(1 for d in DELTA if d is None)
print('delta invalid', nd, 'valid min/max', round(min(d for d in DELTA if d is not None), 4),
      round(max(d for d in DELTA if d is not None), 4))
fill(DELTA)
print('delta after fill min/max', round(min(DELTA), 4), round(max(DELTA), 4))

EPS = 0.008
def r_cut(th_i, z):
    L = rL[th_i]; U = rU[th_i]
    if z <= Z0 - 0.049:
        return L + 0.15
    if z <= Z0:
        return L - EPS
    if z <= ZSEAM:
        t = (z - Z0) / (ZSEAM - Z0)
        return (L - EPS) + t * (U - (L - EPS))
    if z <= ZHI:
        return U + 0.15 * smooth((z - ZSEAM) / (ZHI - ZSEAM))
    return U + 0.15

bm = bmesh.new()
V_in = []
for z in ZS2:
    row = []
    for i, th in enumerate(THS2):
        r = r_cut(i, z)
        a = math.radians(th)
        row.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
    V_in.append(row)
V_out = []
for z in ZS2:
    row = [bm.verts.new((R_OUT2 * math.cos(math.radians(th)), R_OUT2 * math.sin(math.radians(th)), z)) for th in THS2]
    V_out.append(row)
NJ = len(ZS2)
for j in range(NJ - 1):
    for i in range(N):
        k = (i + 1) % N
        bm.faces.new((V_in[j][i], V_in[j][k], V_in[j + 1][k], V_in[j + 1][i]))
        bm.faces.new((V_out[j][i], V_out[j + 1][i], V_out[j + 1][k], V_out[j][k]))
for i in range(N):
    k = (i + 1) % N
    bm.faces.new((V_in[0][i], V_out[0][i], V_out[0][k], V_in[0][k]))
    bm.faces.new((V_in[NJ - 1][i], V_in[NJ - 1][k], V_out[NJ - 1][k], V_out[NJ - 1][i]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
print('CUTTER seam v', len(bm.verts), 'f', len(bm.faces), 'nm',
      sum(1 for e in bm.edges if len(e.link_faces) != 2), 'vol', round(bm.calc_volume(signed=True), 1))
cut_me2 = bpy.data.meshes.new('Seam_Cutter')
bm.to_mesh(cut_me2); bm.free()
cut2 = bpy.data.objects.new('Seam_Cutter', cut_me2)
sc.collection.objects.link(cut2)
cut2.hide_render = True
apply_boolean(body, cut2, 'seamtaper')
cut2.hide_viewport = True
print("=== AFTER SEAM TAPER ===")
audit('SEAM')
dg = bpy.context.evaluated_depsgraph_get()

# smooth shading
bm = bmesh.new(); bm.from_mesh(body.data); bm.normal_update()
for e in bm.edges:
    if len(e.link_faces) != 2 or e.link_faces[0].normal.length < 1e-9 or e.link_faces[1].normal.length < 1e-9:
        e.smooth = False; continue
    if math.degrees(e.link_faces[0].normal.angle(e.link_faces[1].normal)) > 30.0:
        e.smooth = False
for f in bm.faces: f.smooth = True
bm.to_mesh(body.data); bm.free(); body.data.update()

# ================================================================ probes
dg2 = bpy.context.evaluated_depsgraph_get()
def hitX(y, z):
    org = mi @ Vector((60.0, y, z)); d = (M3i @ Vector((-1, 0, 0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=200.0, depsgraph=dg2)
    if not ok: return None
    return (mw @ loc).x
print('seam +X')
ZP = (53.0, 53.2, 53.3, 53.4, 53.6, 53.8, 54.0, 54.2, 54.30, 54.34, 54.35, 54.36, 54.40, 54.45, 54.55, 54.60, 54.65, 55.0, 56.0)
for y in (0.0, -20.0, -30.0, -45.0, -50.0, -52.0, 30.0, 50.0):
    row = []
    for z in ZP:
        v = hitX(y, z); row.append('  --  ' if v is None else f'{v:7.3f}')
    print(f' y{y:6.1f} ' + ' '.join(row))
print('cols ' + ' '.join(f'{z:5.2f}' for z in ZP))

def hitY(x, z, sy=-1):
    org = mi @ Vector((x, sy * 80.0, z)); d = (M3i @ Vector((0, -sy, 0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=200.0, depsgraph=dg2)
    if not ok: return None
    return abs((mw @ loc).y)
print('seam -Y front')
for x in (0.0, 15.0, -25.0):
    row = []
    for z in ZP:
        v = hitY(x, z); row.append('  --  ' if v is None else f'{v:7.3f}')
    print(f' x{x:6.1f} ' + ' '.join(row))
print('seam +Y back')
for x in (0.0, 15.0, -25.0):
    row = []
    for z in ZP:
        v = hitY(x, z, sy=1); row.append('  --  ' if v is None else f'{v:7.3f}')
    print(f' x{x:6.1f} ' + ' '.join(row))
print('dims', tuple(round(v, 3) for v in body.dimensions))
bb = [mw @ Vector(c) for c in body.bound_box]
print('bbox x', round(min(p.x for p in bb), 3), round(max(p.x for p in bb), 3),
      'y', round(min(p.y for p in bb), 3), round(max(p.y for p in bb), 3),
      'z', round(min(p.z for p in bb), 3), round(max(p.z for p in bb), 3))

# ================================================================ renders
sc.render.engine = 'BLENDER_WORKBENCH'
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
        o.hide_render = True
cam_d = bpy.data.cameras.new('C'); cam = bpy.data.objects.new('C', cam_d)
sc.collection.objects.link(cam); sc.camera = cam
def look(pos, tgt, lens):
    cam.location = pos; cam.data.lens = lens
    d = Vector(tgt) - Vector(pos)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
VIEWS = [
    ('b5_q', (150, -120, 80), (36, -58, 47), 80),
    ('b5_sh', (120, -95, 66), (36.5, -59.0, 52.0), 135),
    ('b5_seam', (120, -60, 57.4), (39.0, -50.0, 54.35), 150),
    ('b5_side', (170, -62, 50), (39, -58, 50), 75),
    ('b5_rl', (-150, 120, 80), (-36, 58, 47), 80),
    ('b5_mid', (100, -30, 58), (39, -25, 54.2), 130),
    ('b5_front', (0, -135, 55.2), (0, -64, 54.35), 150),
    ('b5_back', (0, 135, 55.2), (0, 64, 54.35), 150),
]
for tag, pos, tgt, lens in VIEWS:
    look(pos, tgt, lens)
    sc.render.filepath = os.path.join(OUT, f'r5_{tag[3:]}.png')
    bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(cam, do_unlink=True); bpy.data.cameras.remove(cam_d)
cut.hide_viewport = False; cut2.hide_viewport = False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'rev5_stage.blend'))
print('DONE')
