import bpy, bmesh, math, os
from mathutils import Vector
ROOT = r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5'
parts = [
 ('Enclosure_Body.stl', (0, 0, 1), 'body bottom on bed'),
 ('Enclosure_Lid.stl', (0, 0, -1), 'lid top on bed'),
 ('Belly_Pan.stl', (0, 0, 1), 'pan outer on bed'),
 ('Face_Plate.stl', (0, 1, 0), 'face back on bed'),
 ('LED_Diffuser_Ring.stl', (0, 0, 1), 'ring flat on bed'),
 ('Leg_R.stl', (-1, 0, 0), 'leg outer on bed'),
 ('Button_Top.stl', (0, 0, -1), 'button cap on bed'),
 ('Ear_R.stl', (0, 0, 1), 'ear base on bed'),
 ('Tail.stl', (0, 0, 1), 'tail base on bed'),
]
for fname, B, note in parts:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    path = os.path.join(ROOT, 'stl', 'v3', fname)
    bpy.ops.wm.stl_import(filepath=path, global_scale=1.0)
    ob = bpy.context.selected_objects[0]
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.normal_update()
    B = Vector(B).normalized()
    vals = []
    for f in bm.faces:
        n = f.normal
        c = f.calc_center_median()
        vals.append((n.dot(B), f.calc_area(), c.dot(B)))
    mn = min(v[2] for v in vals)
    bed_area = sum(a for d, a, p in vals if p < mn + 0.25 and d < -0.9)
    ov = []
    for d, a, p in vals:
        if p < mn + 0.25:
            continue
        if d < -0.02:
            ang = math.degrees(math.acos(max(-1, min(1, d)))) - 90.0
            ov.append((ang, a))
    ov.sort(reverse=True)
    big = sum(a for ang, a in ov if ang > 45)
    very = sum(a for ang, a in ov if ang > 60)
    maxang = ov[0][0] if ov else 0
    print('%-24s %-18s maxOver=%5.1fdeg  A>45=%8.1f  A>60=%8.1f  bed=%8.1f' % (fname, note, maxang, big, very, bed_area))
    bm.free()
