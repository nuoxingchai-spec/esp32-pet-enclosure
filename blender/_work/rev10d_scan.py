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

for sx, yy in ((-1, 35.3), (-1, 42.1), (-1, 49.1), (-1, 35.8), (1, 35.3), (1, 42.1), (1, 49.1)):
    vals = []
    for k in range(31):
        z = 54.50 + 0.02 * k
        v = cast(sx, -yy, z)
        vals.append((round(z, 2), round(v, 4) if v is not None else None))
    print(f'sx={sx:+d} y={-yy}')
    print('  ' + ' '.join(f'{z:.2f}:{v:.3f}' if v is not None else f'{z:.2f}:MISS' for z, v in vals))
print('DONE')
