import bpy, bmesh, math, os
from mathutils import Vector

ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
OUT = os.path.join(ROOT, r"blender\_work")
F = os.path.join(OUT, 'rev6_corner.blend')
bpy.ops.wm.open_mainfile(filepath=F)
sc = bpy.context.scene
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world; mi = mw.inverted(); M3i = mw.to_3x3().inverted()
dg = bpy.context.evaluated_depsgraph_get()

def audit(tag):
    bm = bmesh.new(); bm.from_mesh(body.data)
    nm = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    bnd = sum(1 for e in bm.edges if len(e.link_faces) < 2)
    zero = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    vol = bm.calc_volume(signed=True)
    print(f"AUDIT {tag:8s} v={len(bm.verts):6d} f={len(bm.faces):6d} nm={nm} bnd={bnd} zero={zero} vol={vol:.1f}")
    bm.free()
    return vol

def cast(sx, y, z):
    org = mi @ Vector((sx * 60.0, y, z))
    d = (M3i @ Vector((-sx, 0.0, 0.0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=200.0, depsgraph=dg)
    if not ok:
        return None
    p = mw @ loc
    return p.x * sx

def smooth(t):
    t = max(0.0, min(1.0, t)); return t * t * (3.0 - 2.0 * t)

VOL0 = audit('BEFORE')
STRIPS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
YS = [26.9 + 0.25 * i for i in range(117)]   # 26.9 .. 55.9
TOP = 54.70
EPS0 = 0.006
EPS_TOP = 0.0006

def epsz(z):
    if z <= 54.55:
        return EPS0
    return EPS0 + (EPS_TOP - EPS0) * smooth((z - 54.55) / (TOP - 54.55))

def beta(yy):
    if yy < 27.9:
        return smooth((yy - 26.9) / 1.0)
    if yy <= 54.9:
        return 1.0
    return smooth((55.9 - yy) / 1.0)

ZROWS = [48.35, 48.9, 49.6, 50.3, 51.0, 51.7, 52.4, 53.1, 53.7, 54.1,
         54.30, 54.55, TOP]

data = {}
for sx, sy in STRIPS:
    W = []; C = []
    for yy in YS:
        y = sy * yy
        w = cast(sx, y, 52.0)
        c = cast(sx, y, 54.55)
        if w is None or c is None or not (37.5 < w < 39.6) or not (37.5 < c < 39.6):
            raise RuntimeError(f'implausible sx={sx} sy={sy} y={y} w={w} c={c}')
        W.append(w); C.append(c)
    data[(sx, sy)] = (W, C)
    print(f"STRIP sx={sx:+d} sy={sy:+d} wall {min(W):.4f}..{max(W):.4f} "
          f"collar {min(C):.4f}..{max(C):.4f} maxdepth={(max(a-b for a,b in zip(W,C))+EPS0)*1000:.1f}um")

bm = bmesh.new()
for sx, sy in STRIPS:
    W, C = data[(sx, sy)]
    inner = []; outer = []
    for i, yy in enumerate(YS):
        y = sy * yy
        b = beta(yy)
        w = W[i]; cref = C[i]
        col_in = []; col_out = []
        for z in ZROWS:
            base = (1.0 - b) * (w + 0.010) + b * (cref - epsz(z))
            if z >= 54.30:
                x = base
            else:
                tz = smooth((z - 48.35) / (54.30 - 48.35))
                x = (w + 0.010) + tz * (base - (w + 0.010))
            col_in.append(bm.verts.new((sx * x, y, z)))
            col_out.append(bm.verts.new((sx * 50.0, y, z)))
        inner.append(col_in); outer.append(col_out)
    NI, NK = len(YS), len(ZROWS)
    for i in range(NI - 1):
        for k in range(NK - 1):
            bm.faces.new((inner[i][k], inner[i + 1][k], inner[i + 1][k + 1], inner[i][k + 1]))
            bm.faces.new((outer[i][k], outer[i][k + 1], outer[i + 1][k + 1], outer[i + 1][k]))
    for i in range(NI - 1):
        bm.faces.new((inner[i][0], outer[i][0], outer[i + 1][0], inner[i + 1][0]))
        bm.faces.new((inner[i][NK - 1], inner[i + 1][NK - 1], outer[i + 1][NK - 1], outer[i][NK - 1]))
    for k in range(NK - 1):
        bm.faces.new((inner[0][k], inner[0][k + 1], outer[0][k + 1], outer[0][k]))
        bm.faces.new((inner[NI - 1][k], outer[NI - 1][k], outer[NI - 1][k + 1], inner[NI - 1][k + 1]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
me = bpy.data.meshes.new('Seam_Cutter')
bm.to_mesh(me); bm.free()
cut = bpy.data.objects.new('Seam_Cutter', me)
sc.collection.objects.link(cut)
cut.hide_render = True
bpy.context.view_layer.objects.active = body
for o in sc.objects:
    o.select_set(False)
body.select_set(True)
mod = body.modifiers.new('seam', 'BOOLEAN')
mod.operation = 'DIFFERENCE'; mod.solver = 'MANIFOLD'; mod.object = cut
bpy.ops.object.modifier_apply(modifier=mod.name)
cut.hide_viewport = True
for p in body.data.polygons:
    p.use_smooth = False
dg = bpy.context.evaluated_depsgraph_get()
VOL1 = audit('TAPER')
print(f"volume delta {VOL1 - VOL0:.2f} mm3  {'OK' if abs(VOL1 - VOL0) < 60 else 'SUSPICIOUS'}")

print('--- post ledge (54.20 vs 54.55) ---')
for sx in (1, -1):
    for y in (30.0, 35.3, 45.0, -30.0, -35.3, -45.0):
        lo = cast(sx, y, 54.20); up = cast(sx, y, 54.55)
        print(f"  sx={sx:+d} y={y:6.1f} lo={lo:.5f} up={up:.5f} d={(lo-up)*1000:6.2f}um")

print('--- post vertical profile ---')
for sx, y in ((1, 45.0), (1, -35.3), (-1, -45.0), (-1, 35.3)):
    vals = []
    for z in (47.5, 48.35, 49.0, 50.0, 51.0, 52.0, 53.0, 54.0, 54.3, 54.55, 54.70, 54.80, 55.2):
        v = cast(sx, y, z)
        vals.append(f'{z:.2f}:{v:.4f}')
    print(f'  sx={sx:+d} y={y}: ' + ' '.join(vals))

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
        o.hide_render = True; o.hide_viewport = True
cam_d = bpy.data.cameras.new('C'); cam = bpy.data.objects.new('C', cam_d)
sc.collection.objects.link(cam); sc.camera = cam
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
    ('seam2', (95, -5, 60), (39, -35, 54.35), 110),
    ('seamL', (-120, 60, 57.4), (-39, 50, 54.35), 150),
]
for tag, pos, tgt, lens in VIEWS:
    look(pos, tgt, lens)
    sc.render.filepath = os.path.join(OUT, f'r10e_{tag}.png')
    bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(cam, do_unlink=True)
bpy.data.cameras.remove(cam_d)
cut.hide_viewport = False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'rev10e_taper.blend'))
print('DONE')
