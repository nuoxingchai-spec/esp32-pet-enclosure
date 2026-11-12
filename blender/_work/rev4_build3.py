import bpy, bmesh, math, os
from mathutils import Vector

ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
OUT = os.path.join(ROOT, r"blender\_work")
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT, 'rev4_stage.blend'))
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
    print(f"AUDIT {tag:6s} v={len(bm.verts)} f={len(bm.faces)} nm={nm} bnd={bnd} zero={zero} comps={comps} vol={vol:.1f}")
    bm.free()
    return nm, bnd, zero, comps

audit('BEFORE')

def smooth(t):
    t = max(0.0, min(1.0, t)); return t * t * (3.0 - 2.0 * t)

YS = [-57.0 + 0.5 * i for i in range(229)]
ZS = [53.0 + 0.2 * i for i in range(9)]      # 53.0..54.6
ZS += [54.7, 55.0, 56.0, 57.0, 58.0, 59.0, 60.0]
R_OUT = 46.0
Z0, Z1 = 53.0, 54.6

def ray_side(sx, y, z, back=60.0):
    org = mi @ Vector((sx * back, y, z))
    d = (M3i @ Vector((-sx, 0.0, 0.0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=200.0, depsgraph=dg)
    if not ok: return None
    return abs((mw @ loc).x)

bm = bmesh.new()
for sx in (1, -1):
    xl = {}; xu = {}
    miss = 0
    for y in YS:
        a = ray_side(sx, y, 53.0); b = ray_side(sx, y, 55.0)
        if a is None or b is None:
            miss += 1
            a = 42.0 if a is None else a
            b = 42.0 if b is None else b
        xl[y] = a; xu[y] = b
    print('side', sx, 'miss', miss, 'xL', round(min(xl.values()), 3), round(max(xl.values()), 3),
          'xU', round(min(xu.values()), 3), round(max(xu.values()), 3))
    rows = []
    for z in ZS:
        row = []
        for y in YS:
            fade = 0.05 * smooth((abs(y) - 52.0) / 5.0)
            if z <= Z1:
                s = smooth((z - Z0) / (Z1 - Z0))
                eps = 0.005 + (0.0015 - 0.005) * smooth((z - Z0) / (Z1 - Z0))
                x = xl[y] + s * (xu[y] - xl[y]) + eps + fade
            else:
                x = xu[y] + 0.12 + fade
            row.append((sx * x, y, z))
        rows.append(row)
    NJ, NY = len(ZS), len(YS)
    V_in = [[bm.verts.new(p) for p in row] for row in rows]
    V_out = [[bm.verts.new((sx * R_OUT, y, z)) for y in YS] for z in ZS]
    for j in range(NJ - 1):
        for i in range(NY - 1):
            bm.faces.new((V_in[j][i], V_in[j][i + 1], V_in[j + 1][i + 1], V_in[j + 1][i]))
            bm.faces.new((V_out[j][i], V_out[j + 1][i], V_out[j + 1][i + 1], V_out[j][i + 1]))
    for i in range(NY - 1):
        bm.faces.new((V_in[0][i], V_out[0][i], V_out[0][i + 1], V_in[0][i + 1]))
        bm.faces.new((V_in[NJ - 1][i], V_in[NJ - 1][i + 1], V_out[NJ - 1][i + 1], V_out[NJ - 1][i]))
    for j in range(NJ - 1):
        bm.faces.new((V_in[j][0], V_in[j + 1][0], V_out[j + 1][0], V_out[j][0]))
        bm.faces.new((V_in[j][NY - 1], V_out[j][NY - 1], V_out[j + 1][NY - 1], V_in[j + 1][NY - 1]))

bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
print('CUTTER v', len(bm.verts), 'f', len(bm.faces),
      'nm', sum(1 for e in bm.edges if len(e.link_faces) != 2),
      'vol', round(bm.calc_volume(signed=True), 1))
cut_me = bpy.data.meshes.new('Side_Cutter')
bm.to_mesh(cut_me); bm.free()
cut = bpy.data.objects.new('Side_Cutter', cut_me)
sc.collection.objects.link(cut); cut.hide_render = True

bpy.context.view_layer.objects.active = body
for o in sc.objects: o.select_set(False)
body.select_set(True)
mod = body.modifiers.new('sideseam', 'BOOLEAN')
mod.operation = 'DIFFERENCE'; mod.solver = 'MANIFOLD'; mod.object = cut
try:
    bpy.ops.object.modifier_apply(modifier=mod.name)
    print('APPLIED manifold')
except Exception as e:
    print('MANIFOLD failed:', e)
    body.modifiers.clear()
    mod = body.modifiers.new('sideseam', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'; mod.solver = 'EXACT'; mod.object = cut
    bpy.ops.object.modifier_apply(modifier=mod.name)
    print('APPLIED exact')
cut.hide_viewport = True
audit('AFTER')

# smooth shading
bm = bmesh.new(); bm.from_mesh(body.data); bm.normal_update()
for e in bm.edges:
    if len(e.link_faces) != 2 or e.link_faces[0].normal.length < 1e-9 or e.link_faces[1].normal.length < 1e-9:
        e.smooth = False; continue
    if math.degrees(e.link_faces[0].normal.angle(e.link_faces[1].normal)) > 30.0:
        e.smooth = False
for f in bm.faces: f.smooth = True
bm.to_mesh(body.data); bm.free(); body.data.update()

# probes
dg2 = bpy.context.evaluated_depsgraph_get()
def hitX(y, z):
    org = mi @ Vector((60.0, y, z)); d = (M3i @ Vector((-1, 0, 0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=200.0, depsgraph=dg2)
    if not ok: return None
    return (mw @ loc).x
print('seam +X')
for y in (0.0, -20.0, -30.0, -45.0, -52.0):
    row = []
    for z in (53.0, 53.5, 54.0, 54.30, 54.35, 54.40, 54.55, 54.60, 54.65, 55.0, 56.0):
        v = hitX(y, z); row.append('  --  ' if v is None else f'{v:7.3f}')
    print(f' y{y:6.1f} ' + ' '.join(row))
print('cols z53.0 53.5 54.0 54.30 54.35 54.40 54.55 54.60 54.65 55.0 56.0')
print('dims', tuple(round(v, 3) for v in body.dimensions))

# renders
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
    ('b3_q', (150, -120, 80), (36, -58, 47), 80),
    ('b3_sh', (120, -95, 66), (36.5, -59.0, 52.0), 135),
    ('b3_seam', (120, -60, 57.4), (39.0, -50.0, 54.35), 150),
    ('b3_side', (170, -62, 50), (39, -58, 50), 75),
    ('b3_rl', (-150, 120, 80), (-36, 58, 47), 80),
    ('b3_mid', (100, -30, 58), (39, -25, 54.2), 130),
]
for tag, pos, tgt, lens in VIEWS:
    look(pos, tgt, lens)
    sc.render.filepath = os.path.join(OUT, f'r4_{tag}.png')
    bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(cam, do_unlink=True); bpy.data.cameras.remove(cam_d)
cut.hide_viewport = False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'rev4_stage3.blend'))
print('DONE')
