import bpy, math
from mathutils import Vector
ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
for name, path in [('CLEAN', r"blender\robot_dog_enclosure_v3.blend"), ('CUT', r"blender\_work\rev6_corner.blend")]:
    bpy.ops.wm.open_mainfile(filepath=ROOT + "\\" + path)
    body = bpy.data.objects['Enclosure_Body']
    mw = body.matrix_world; mi = mw.inverted(); M3i = mw.to_3x3().inverted()
    dg = bpy.context.evaluated_depsgraph_get()
    def rx(y, z):
        org = mi @ Vector((60.0, y, z)); d = (M3i @ Vector((-1, 0, 0))).normalized()
        ok, loc, nor, idx = body.ray_cast(org, d, distance=200.0, depsgraph=dg)
        return None if not ok else round((mw @ loc).x, 4)
    print("==", name)
    for y in (-55.0, -50.0, -45.0, -40.0, -35.0, -30.0, -25.0, -20.0):
        row = []
        for z in (53.8, 54.0, 54.2, 54.3, 54.34, 54.36, 54.4, 54.45, 54.5, 54.6):
            v = rx(y, z); row.append("  --  " if v is None else f"{v:6.3f}")
        print(f" y{y:6.1f} " + " ".join(row))
    print(" z       53.80 54.00 54.20 54.30 54.34 54.36 54.40 54.45 54.50 54.60")
