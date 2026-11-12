import bpy, bmesh, math, os
from mathutils import Vector
ROOT = r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=os.path.join(ROOT, 'stl', 'v3', 'Enclosure_Body.stl'), global_scale=1.0)
ob = bpy.context.selected_objects[0]
bm = bmesh.new(); bm.from_mesh(ob.data); bm.normal_update()
for label, Bv in [('+Z bottom-down', (0, 0, 1)), ('-Z top-down', (0, 0, -1)),
                  ('+X right side down', (1, 0, 0)), ('-X left side down', (-1, 0, 0)),
                  ('+Y front down', (0, 1, 0)), ('-Y back down', (0, -1, 0))]:
    B = Vector(Bv).normalized()
    mn = min(f.calc_center_median().dot(B) for f in bm.faces)
    over = 0; contact = 0; mx = 0
    for f in bm.faces:
        d = f.normal.dot(B); c = f.calc_center_median(); a = f.calc_area()
        if c.dot(B) < mn + 0.25:
            if d < -0.9: contact += a
            continue
        if d < -0.02:
            ang = math.degrees(math.acos(max(-1, min(1, d)))) - 90.0
            if ang > 45: over += a
            mx = max(mx, ang)
    print('%-20s contact=%7.1f  over45=%7.1f  max=%4.1f' % (label, contact, over, mx))
bm.free()
