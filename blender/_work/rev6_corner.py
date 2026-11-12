import bpy, bmesh, math, os
from mathutils import Vector

ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
OUT = os.path.join(ROOT, r"blender\_work")
F = os.path.join(ROOT, r"blender\robot_dog_enclosure_v3.blend")
bpy.ops.wm.open_mainfile(filepath=F)
sc = bpy.context.scene
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world; mi = mw.inverted()
M3i = mw.to_3x3().inverted()
dg = bpy.context.evaluated_depsgraph_get()

def audit(tag):
    bm = bmesh.new(); bm.from_mesh(body.data)
    nm = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    bnd = sum(1 for e in bm.edges if len(e.link_faces) < 2)
    zero = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    vol = bm.calc_volume(signed=True)
    print(f"AUDIT {tag:8s} v={len(bm.verts):6d} f={len(bm.faces):6d} nm={nm} bnd={bnd} zero={zero} vol={vol:.1f}")
    bm.free()

def smooth(t):
    t = max(0.0, min(1.0, t)); return t * t * (3.0 - 2.0 * t)

CORNERS = [('FR', 30.0, -55.0, 1, -1), ('FL', -30.0, -55.0, -1, -1),
           ('RR', 30.0, 55.0, 1, 1),  ('RL', -30.0, 55.0, -1, 1)]
THS = [-15 + i for i in range(81)]
ZS = [49.0 + 0.35 * i for i in range(16)] + [54.30, 54.34, 54.35, 54.36, 54.50, 55.0, 56.0, 57.0, 58.0, 59.0, 60.0]
R_OUT = 42.0

def clear(th):
    if th < 0.0: return 0.12 * smooth(-th / 15.0)
    if th > 44.5: return 0.12 * smooth((th - 44.5) / 20.5)
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
                r = rl[th] + smooth((z - 49.0) / 5.35) * (ru[th] - rl[th]) + clear(th)
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
cut_me = bpy.data.meshes.new('Shoulder_Cutter')
bm.to_mesh(cut_me); bm.free()
cut = bpy.data.objects.new('Shoulder_Cutter', cut_me)
sc.collection.objects.link(cut); cut.hide_render = True
bpy.context.view_layer.objects.active = body
for o in sc.objects: o.select_set(False)
body.select_set(True)
mod = body.modifiers.new('shoulder', 'BOOLEAN')
mod.operation = 'DIFFERENCE'; mod.solver = 'MANIFOLD'; mod.object = cut
bpy.ops.object.modifier_apply(modifier=mod.name)
cut.hide_viewport = True
audit('CORNER')
print('smooth polys after boolean', sum(1 for p in body.data.polygons if p.use_smooth), 'of', len(body.data.polygons))
print('sharp edges after boolean', sum(1 for e in body.data.edges if e.use_edge_sharp), 'of', len(body.data.edges))

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
]
for tag, pos, tgt, lens in VIEWS:
    look(pos, tgt, lens)
    sc.render.filepath = os.path.join(OUT, f'r6_flat_{tag}.png')
    bpy.ops.render.render(write_still=True)

bm = bmesh.new(); bm.from_mesh(body.data); bm.normal_update()
for e in bm.edges:
    if len(e.link_faces) != 2 or e.link_faces[0].normal.length < 1e-9 or e.link_faces[1].normal.length < 1e-9:
        e.smooth = False; continue
    if math.degrees(e.link_faces[0].normal.angle(e.link_faces[1].normal)) > 30.0:
        e.smooth = False
for f in bm.faces: f.smooth = True
bm.to_mesh(body.data); bm.free(); body.data.update()
for tag, pos, tgt, lens in VIEWS:
    look(pos, tgt, lens)
    sc.render.filepath = os.path.join(OUT, f'r6_sm_{tag}.png')
    bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(cam, do_unlink=True); bpy.data.cameras.remove(cam_d)
cut.hide_viewport = False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'rev6_corner.blend'))
print('DONE')
