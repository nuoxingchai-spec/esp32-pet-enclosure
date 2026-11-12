import bpy, bmesh, math, os
from mathutils import Vector

ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
OUT = os.path.join(ROOT, r"blender\_work")
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, r"blender\robot_dog_enclosure_v3.blend"))
sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()

# ---------------------------------------------------------------- button mesh
btn = bpy.data.objects['Button_Top_1']
me = btn.data
print('BTN mesh', me.name, 'users', me.users, 'materials', [m.name if m else None for m in me.materials])

def profile_points():
    P = [(0.0, 8.85)]
    for i in range(1, 11):                      # dome, theta 90 -> 0
        th = math.radians(90.0 - i * 9.0)
        P.append((2.075 * math.cos(th), 8.45 + 0.40 * math.sin(th)))
    P += [(2.075, 7.80), (1.875, 7.60), (1.80, 7.60)]   # cap side + lead-in
    P += [(1.80, 1.30)]                                  # rod
    for i in range(1, 5):                                # fillet R0.3 rod->flange
        ph = math.radians(180.0 + i * 22.5)
        P.append((2.10 + 0.30 * math.cos(ph), 1.30 + 0.30 * math.sin(ph)))
    P += [(2.80, 1.00), (2.80, 0.20), (2.60, 0.00), (0.0, 0.00)]
    return P

def rebuild_button():
    P = profile_points()
    SEG = 96
    ang = [2.0 * math.pi * j / SEG for j in range(SEG)]
    bm = bmesh.new()
    rings = []
    for (r, z) in P:
        if r < 1e-9:
            rings.append(('pole', bm.verts.new((0.0, 0.0, z))))
        else:
            rings.append(('ring', [bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for a in ang]))
    for k in range(len(rings) - 1):
        t0, a0 = rings[k]; t1, a1 = rings[k + 1]
        if t0 == 'pole' and t1 == 'ring':
            for j in range(SEG):
                bm.faces.new((a0, a1[j], a1[(j + 1) % SEG]))
        elif t0 == 'ring' and t1 == 'pole':
            for j in range(SEG):
                bm.faces.new((a0[j], a1, a0[(j + 1) % SEG]))
        elif t0 == 'ring' and t1 == 'ring':
            for j in range(SEG):
                bm.faces.new((a0[j], a0[(j + 1) % SEG], a1[(j + 1) % SEG], a1[j]))
        else:
            raise RuntimeError('pole-pole segment')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        f.smooth = True
    sharp = 0
    for e in bm.edges:
        if len(e.link_faces) == 2:
            n0, n1 = e.link_faces[0].normal, e.link_faces[1].normal
            if n0.length > 0 and n1.length > 0 and n0.angle(n1) > math.radians(35.0):
                e.smooth = False; sharp += 1
    bm.to_mesh(me)
    bm.free()
    me.update()
    print(f'BTN rebuilt v={len(me.vertices)} f={len(me.polygons)} sharp={sharp}')

rebuild_button()
bpy.context.view_layer.update()

bm = bmesh.new(); bm.from_mesh(me)
print(f"BTN AUDIT v={len(bm.verts)} f={len(bm.faces)} "
      f"nm={sum(1 for e in bm.edges if len(e.link_faces) != 2)} "
      f"bnd={sum(1 for e in bm.edges if len(e.link_faces) < 2)} "
      f"zero={sum(1 for f in bm.faces if f.calc_area() < 1e-9)} vol={bm.calc_volume(signed=True):.2f}")
bm.free()
print('BTN dims', tuple(round(v, 3) for v in btn.dimensions))

# cap profile check
for zi in (7.0, 7.6, 7.7, 7.9, 8.2, 8.4, 8.6, 8.8, 8.84):
    bb = bmesh.new(); bb.from_mesh(me)
    radii = [v.co.xy.length for v in bb.verts if abs(v.co.z - zi) < 0.02]
    print(f'  z={zi:.2f} r={max(radii) if radii else float("nan"):.3f}')
    bb.free()

# ---------------------------------------------------------------- lid seat fill + new holes
lid = bpy.data.objects['Enclosure_Lid']
CENTERS = [(-24.83, -35.47), (-24.83, -42.45), (-24.83, -49.47)]

def cyl_mesh(name, r, z0, z1, seg=128):
    bm = bmesh.new()
    for (x, y) in CENTERS:
        ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                                    radius1=r, radius2=r, depth=(z1 - z0))
        bmesh.ops.translate(bm, vec=(x, y, (z0 + z1) * 0.5), verts=ret['verts'])
    m = bpy.data.meshes.new(name); bm.to_mesh(m); bm.free()
    o = bpy.data.objects.new(name, m); sc.collection.objects.link(o)
    return o

fill = cyl_mesh('LidFill', 2.475, 66.65, 67.0)
holes = cyl_mesh('LidHoles', 2.2, 64.40, 67.10)

for o in sc.objects:
    o.select_set(False)
lid.select_set(True)
bpy.context.view_layer.objects.active = lid
for ob, op, tag in ((fill, 'UNION', 'fill'), (holes, 'DIFFERENCE', 'holes')):
    md = lid.modifiers.new(tag, 'BOOLEAN')
    md.operation = op; md.solver = 'MANIFOLD'; md.object = ob
    bpy.ops.object.modifier_apply(modifier=md.name)
    print('LID boolean applied', tag)
for ob in (fill, holes):
    bpy.data.objects.remove(ob, do_unlink=True)

bm = bmesh.new(); bm.from_mesh(lid.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(lid.data); bm.free()
for p in lid.data.polygons:
    p.use_smooth = False
lid.data.update()
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()

bm = bmesh.new(); bm.from_mesh(lid.data)
print(f"LID AUDIT v={len(bm.verts)} f={len(bm.faces)} "
      f"nm={sum(1 for e in bm.edges if len(e.link_faces) != 2)} "
      f"bnd={sum(1 for e in bm.edges if len(e.link_faces) < 2)} "
      f"zero={sum(1 for f in bm.faces if f.calc_area() < 1e-9)} vol={bm.calc_volume(signed=True):.2f}")
bm.free()
print('LID dims', tuple(round(v, 3) for v in lid.dimensions))

def lcast(x, y, z, d, dist=40.0):
    ok, loc, nor, idx = lid.ray_cast(Vector((x, y, z)), Vector(d), distance=dist, depsgraph=dg)
    return (loc.copy(), nor.copy()) if ok else (None, None)

print('--- lid top map after fill (local z) ---')
for (cx, cy) in CENTERS:
    row = []
    for r in (0.0, 1.0, 2.0, 2.15, 2.2, 2.3, 2.45, 2.6, 3.0, 5.0):
        loc, nor = lcast(cx + r, cy, 58.0, (0, 0, -1), 12.0)
        row.append('PASS' if loc is None else f"{loc.z:4.1f}")
    print(f'  {cx},{cy}: ' + ' '.join(row))

print('--- button/lid clearance probes (world) ---')
for (cx, cy) in CENTERS:
    org = Vector((cx + 2.15, cy, 55.0))
    ok, loc, nor, idx = lid.ray_cast(Vector((org.x, org.y, 58.0)), Vector((0, 0, 1)), distance=15.0, depsgraph=dg)
    print(f'  hole wall probe x={org.x:.2f}: ' + ('open' if not ok else f'z={loc.z:.2f}'))

print('--- button vs lid rest overlap ---')
import bmesh
def bvh_overlap(a, b):
    from mathutils.bvhtree import BVHTree
    da = a.evaluated_get(dg).to_mesh(); db = b.evaluated_get(dg).to_mesh()
    bma = bmesh.new(); bma.from_mesh(da)
    bmb = bmesh.new(); bmb.from_mesh(db)
    ta = BVHTree.FromBMesh(bma); tb = BVHTree.FromBMesh(bmb)
    pairs = ta.overlap(tb)
    a.evaluated_get(dg).to_mesh_clear(); b.evaluated_get(dg).to_mesh_clear()
    bma.free(); bmb.free()
    return len(pairs)
for y in (-35.47, -42.45, -49.47):
    ob = bpy.data.objects['Button_Top_' + { -35.47:'1', -42.45:'2', -49.47:'3'}[y]]
    print(f'  button y={y}: lid-tri pairs={bvh_overlap(ob, lid)}')

sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading
sh.light = 'STUDIO'; sh.studio_light = 'Default'; sh.color_type = 'OBJECT'
sh.show_cavity = True; sh.cavity_type = 'BOTH'
sh.curvature_ridge_factor = 1.0; sh.curvature_valley_factor = 1.0
sh.show_shadows = True; sh.shadow_intensity = 0.5
sh.show_object_outline = False
sc.world.color = (0.045, 0.045, 0.055)
sc.render.image_settings.file_format = 'PNG'
sc.view_settings.view_transform = 'Standard'
sc.render.resolution_x = 1400; sc.render.resolution_y = 1400
COL = {'Enclosure_Body': (0.84,0.84,0.82,1), 'Enclosure_Lid': (0.76,0.76,0.74,1),
       'Button_Top_1': (0.97,0.97,0.94,1), 'Button_Top_2': (0.97,0.97,0.94,1),
       'Button_Top_3': (0.97,0.97,0.94,1), 'PCB_Board': (0.10,0.40,0.22,1),
       'PCB_Components': (0.20,0.56,0.30,1)}
for n, c in COL.items():
    o = bpy.data.objects.get(n)
    if o: o.color = c
for o in sc.objects:
    if o.type == 'LIGHT' or o.type == 'CAMERA': o.hide_render = True
    if o.type == 'MESH' and o.name != 'Enclosure_Lid' and not o.name.startswith('Button_Top'):
        o.hide_render = True
cam_d = bpy.data.cameras.new('C'); cam = bpy.data.objects.new('C', cam_d)
sc.collection.objects.link(cam); sc.camera = cam
def look(pos, tgt, lens=55):
    cam.location = pos; cam.data.lens = lens
    cam.rotation_euler = (Vector(tgt) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 30
look((-24.83, -42.45, 190), (-24.83, -42.45, 66))
sc.render.filepath = os.path.join(OUT, 'test_buttons_top.png')
bpy.ops.render.render(write_still=True)
cam.data.ortho_scale = 22
look((-80, -110, 95), (-19, -42, 66.8))
sc.render.filepath = os.path.join(OUT, 'test_buttons_34.png')
bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(cam, do_unlink=True)
bpy.data.cameras.remove(cam_d)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'rev13_smooth.blend'))
print('SAVED rev13_smooth.blend')
print('DONE')
