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

for sx in (1, -1):
    for sy in (-1, 1):
        print(f'=== strip sx={sx:+d} sy={sy:+d}')
        for z in (50.0, 52.0, 54.20, 54.55, 55.0, 55.5, 56.0, 56.5, 57.5, 58.5, 59.3, 59.8):
            bad = []
            for i in range(0, 129):
                yy = 25.0 + 0.25 * i
                y = sy * yy
                v = cast(sx, y, z)
                if v is None or v < 36.0:
                    bad.append(yy)
            runs = []
            for v in bad:
                if runs and abs(v - runs[-1][1]) <= 0.26:
                    runs[-1][1] = v
                else:
                    runs.append([v, v])
            print(f'  z={z:5.2f} bad={[(round(a,2), round(b,2)) for a, b in runs]}')
print('DONE')
