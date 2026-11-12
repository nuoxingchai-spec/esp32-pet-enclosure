import bpy, os, math
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

print('--- ledge profile per strip (lo z=54.20, up z=54.55) ---')
for sx in (1, -1):
    for sy in (1, -1):
        print(f'STRIP sx={sx:+d} sy={sy:+d}')
        for i in range(0, 66):
            yy = 25.0 + 0.5 * i
            y = sy * yy
            lo = cast(sx, y, 54.20); up = cast(sx, y, 54.55)
            if lo is None or up is None:
                print(f'  y={y:7.2f} MISS')
                continue
            d = (lo - up) * 1000.0
            if yy <= 31.0 or yy >= 51.0 or (i % 8 == 0):
                print(f'  y={y:7.2f} lo={lo:.5f} up={up:.5f} d={d:6.1f}um')

print('--- vertical profile +X y=45 / y=-45 ---')
for y in (45.0, -45.0):
    print(f'  y={y}')
    for i in range(0, 25):
        z = 53.90 + 0.05 * i
        x = cast(1, y, z)
        print(f'    z={z:6.2f} x={x:.5f}')
print('DONE')
