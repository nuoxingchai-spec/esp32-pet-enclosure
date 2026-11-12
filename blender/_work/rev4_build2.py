import bpy, bmesh, math, os
from mathutils import Vector

ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
F = os.path.join(ROOT, r"blender\robot_dog_enclosure_v3.blend")
OUT = os.path.join(ROOT, r"blender\_work")

bpy.ops.wm.open_mainfile(filepath=F)
sc = bpy.context.scene
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world; mi = mw.inverted()
M3 = mw.to_3x3(); M3i = M3.inverted()
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
    print(f"AUDIT {tag:8s} v={len(bm.verts):6d} f={len(bm.faces):6d} nm={nm} bnd={bnd} zero={zero} comps={comps} vol={vol:.1f}")
    bm.free()

print("=== BEFORE ===")
audit(body, 'BODY')

def smooth(t):
    t = max(0.0, min(1.0, t)); return t * t * (3.0 - 2.0 * t)

N = 360
PH = [2.0 * math.pi * i / N for i in range(N)]
ZS = [49.0 + 0.35 * i for i in range(16)]     # 49.00..54.25
ZS += [54.30, 54.34, 54.35, 54.36, 54.50, 55.0, 56.0, 57.0, 58.0, 59.0, 60.0]
R_OUT = 90.0
ZSEAM = 54.35
EPS_LO, EPS_HI = 0.010, 0.0015

def ray_r(phi, z, back=110.0):
    ux, uy = math.cos(phi), math.sin(phi)
    org = mi @ Vector((back * ux, back * uy, z))
    d = (M3i @ Vector((-ux, -uy, 0.0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=400.0, depsgraph=dg)
    if not ok: return None
    p = mw @ loc
    return math.hypot(p.x, p.y)

rl = []; ru = []
miss = []
for phi in PH:
    a = ray_r(phi, 52.0); b = ray_r(phi, 56.0)
    if a is None or b is None:
        miss.append((round(math.degrees(phi),1), a, b))
        a = a if a is not None else 0.0
        b = b if b is not None else 0.0
    rl.append(a); ru.append(b)
print('MISSES', miss[:40], 'count', len(miss))
for i in range(N):
    if rl[i] == 0.0 or ru[i] == 0.0:
        j = (i-1) % N; k = (i+1) % N
        if rl[i] == 0.0: rl[i] = (rl[j] + rl[k]) * 0.5
        if ru[i] == 0.0: ru[i] = (ru[j] + ru[k]) * 0.5
print('rL range', round(min(rl), 3), round(max(rl), 3), ' rU range', round(min(ru), 3), round(max(ru), 3))

def radius(i, z):
    if z <= ZSEAM:
        t = (z - 49.0) / 5.35
        eps = EPS_LO + (EPS_HI - EPS_LO) * smooth(t)
        return rl[i] + smooth(t) * (ru[i] - rl[i]) + eps
    return ru[i] + 0.12

bm = bmesh.new()
V_in = []
V_out = []
for z in ZS:
    V_in.append([bm.verts.new((radius(i, z) * math.cos(PH[i]),
                               radius(i, z) * math.sin(PH[i]), z)) for i in range(N)])
    V_out.append([bm.verts.new((R_OUT * math.cos(PH[i]), R_OUT * math.sin(PH[i]), z)) for i in range(N)])
NJ = len(ZS)
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
print('CUTTER v', len(bm.verts), 'f', len(bm.faces),
      'nm', sum(1 for e in bm.edges if len(e.link_faces) != 2),
      'vol', round(bm.calc_volume(signed=True), 1))
cut_me = bpy.data.meshes.new('Seam_Cutter')
bm.to_mesh(cut_me); bm.free()
cut = bpy.data.objects.new('Seam_Cutter', cut_me)
sc.collection.objects.link(cut)
cut.hide_render = True

bpy.context.view_layer.objects.active = body
for o in sc.objects: o.select_set(False)
body.select_set(True)
mod = body.modifiers.new('seam', 'BOOLEAN')
mod.operation = 'DIFFERENCE'; mod.solver = 'MANIFOLD'; mod.object = cut
try:
    bpy.ops.object.modifier_apply(modifier=mod.name)
    print('APPLIED manifold')
except Exception as e:
    print('MANIFOLD failed:', e)
    body.modifiers.clear()
    mod = body.modifiers.new('seam', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'; mod.solver = 'EXACT'; mod.object = cut
    bpy.ops.object.modifier_apply(modifier=mod.name)
    print('APPLIED exact')
cut.hide_viewport = True
print("=== AFTER CUT ===")
audit(body, 'CUT')

# smooth-by-angle shading on body
bm = bmesh.new(); bm.from_mesh(body.data); bm.normal_update()
for e in bm.edges:
    if len(e.link_faces) != 2 or e.link_faces[0].normal.length < 1e-9 or e.link_faces[1].normal.length < 1e-9:
        e.smooth = False; continue
    if math.degrees(e.link_faces[0].normal.angle(e.link_faces[1].normal)) > 30.0:
        e.smooth = False
for f in bm.faces: f.smooth = True
bm.to_mesh(body.data); bm.free(); body.data.update()

# seam probes
dg2 = bpy.context.evaluated_depsgraph_get()
def hitX(y, z):
    org = mi @ Vector((60.0, y, z)); d = (M3i @ Vector((-1, 0, 0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=200.0, depsgraph=dg2)
    if not ok: return None
    p = mw @ loc
    return p.x
def hitY(x, z):
    org = mi @ Vector((x, -80.0, z)); d = (M3i @ Vector((0, 1, 0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=200.0, depsgraph=dg2)
    if not ok: return None
    p = mw @ loc
    return p.y
print('seam side +X')
for y in (0.0, -20.0, -30.0, -45.0, -52.0):
    row = []
    for z in (54.30, 54.34, 54.35, 54.36, 54.40, 54.55, 55.0):
        v = hitX(y, z); row.append('  --  ' if v is None else f'{v:7.3f}')
    print(f' y{y:6.1f} ' + ' '.join(row))
print('cols z54.30 54.34 54.35 54.36 54.40 54.55 55.0')
print('seam front -Y')
for x in (0.0, 20.0, -20.0):
    row = []
    for z in (54.30, 54.34, 54.35, 54.36, 54.40, 54.55, 55.0):
        v = hitY(x, z); row.append('  --  ' if v is None else f'{v:7.3f}')
    print(f' x{x:6.1f} ' + ' '.join(row))
print('bbox dims', tuple(round(v, 3) for v in body.dimensions))

# render
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
    ('b2_q', (150, -120, 80), (36, -58, 47), 80),
    ('b2_sh', (120, -95, 66), (36.5, -59.0, 52.0), 135),
    ('b2_seam', (120, -60, 57.4), (39.0, -50.0, 54.35), 150),
    ('b2_side', (170, -62, 50), (39, -58, 50), 75),
    ('b2_rl', (-150, 120, 80), (-36, 58, 47), 80),
]
for tag, pos, tgt, lens in VIEWS:
    look(pos, tgt, lens)
    sc.render.filepath = os.path.join(OUT, f'r4_{tag}.png')
    bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(cam, do_unlink=True); bpy.data.cameras.remove(cam_d)
cut.hide_viewport = False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'rev4_stage2.blend'))
print('DONE')
