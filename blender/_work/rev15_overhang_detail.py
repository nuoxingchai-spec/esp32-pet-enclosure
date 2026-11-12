import bpy, bmesh, math, os
from mathutils import Vector
ROOT = r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5'
parts = [('Enclosure_Body.stl', (0, 0, 1)), ('Enclosure_Lid.stl', (0, 0, -1)),
         ('LED_Diffuser_Ring.stl', (0, 0, 1))]
for fname, B in parts:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=os.path.join(ROOT, 'stl', 'v3', fname), global_scale=1.0)
    ob = bpy.context.selected_objects[0]
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.normal_update()
    B = Vector(B).normalized()
    faces = []
    mn = min(f.calc_center_median().dot(B) for f in bm.faces)
    for f in bm.faces:
        d = f.normal.dot(B); c = f.calc_center_median(); a = f.calc_area()
        if c.dot(B) < mn + 0.25: continue
        if d < -0.02:
            ang = math.degrees(math.acos(max(-1, min(1, d)))) - 90.0
            faces.append((a, ang, c.copy()))
    faces.sort(reverse=True)
    print('PART', fname, 'total>45', round(sum(a for a, ang, c in faces if ang > 45), 1))
    for a, ang, c in faces[:8]:
        print('  face area %.1f ang %.1f center (%.1f, %.1f, %.1f)' % (a, ang, c.x, c.y, c.z))
    bands = {}
    for a, ang, c in faces:
        if ang > 45:
            k = int(c.z // 5) * 5
            bands[k] = bands.get(k, 0) + a
    print('  z bands:', sorted(bands.items()))
    bm.free()
