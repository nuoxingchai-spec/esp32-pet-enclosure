import bpy, os
from mathutils import Vector

ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
OUT = os.path.join(ROOT, r"blender\_work")
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT, 'rev6_corner.blend'))
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world; mi = mw.inverted(); M3i = mw.to_3x3().inverted()
dg = bpy.context.evaluated_depsgraph_get()

def cast(sx, y, z):
    org = mi @ Vector((sx * 60.0, y, z))
    d = (M3i @ Vector((-sx, 0.0, 0.0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=200.0, depsgraph=dg)
    if not ok:
        return None
    p = mw @ loc
    return p.x * sx

for sx in (-1, 1):
    sy = -1
    print(f'=== front strip sx={sx:+d}')
    for z in (54.20, 54.55, 55.0, 55.10, 55.20, 55.25, 55.35):
        out = []
        for i in range(117):
            yy = 26.9 + 0.25 * i
            v = cast(sx, sy * yy, z)
            if v is not None and v < 38.94:
                out.append((round(yy, 2), round(v, 4)))
        print(f'  z={z:5.2f} low={out}')
print('DONE')
