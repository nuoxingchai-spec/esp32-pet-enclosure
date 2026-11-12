import bpy
from mathutils import Vector

F = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob = bpy.data.objects['Enclosure_Body']
mw = ob.matrix_world
mi = mw.inverted()
dg = bpy.context.evaluated_depsgraph_get()


def hit(side, y, z):
    org = mi @ Vector((60.0 * side, y, z))
    d = (mw.to_3x3().inverted() @ Vector((-side, 0, 0))).normalized()
    ok, loc, nor, idx = ob.ray_cast(org, d, distance=200.0, depsgraph=dg)
    if not ok:
        return None
    return (mw @ loc).x


def sym(side, x):
    if x is None:
        return ' '
    a = side * x
    if a >= 39.15:
        return '#'
    if a >= 38.90:
        return '='
    if a >= 38.40:
        return '-'
    if a >= 37.60:
        return '+'
    if a >= 36.50:
        return '.'
    return 'o'


for side, label in ((1, 'RIGHT +X'), (-1, 'LEFT -X')):
    print('=' * 70)
    print(label, ' y from -64 to 64 (1mm), z from 60 down to 20 (1mm)')
    hdr = '      ' + ''.join(str(abs(y) // 10 % 10) if y % 10 == 0 else ' ' for y in range(-64, 65))
    print(hdr)
    for z in range(60, 19, -1):
        row = []
        for y in range(-64, 65):
            row.append(sym(side, hit(side, y + 0.0, z + 0.0)))
        print(f'z{z:3d}  ' + ''.join(row))

# precise fin cross sections on the right side, near the front and rear hips
print('=' * 70)
print('Fine sections: x(y) at fixed z, right side')
for z in (52.0, 50.0, 48.0, 45.0, 42.0, 40.0, 36.0, 30.0, 24.0):
    vals = []
    y = -63.0
    while y <= 63.0:
        x = hit(1, y, z)
        if x is not None and x > 36.0:
            vals.append((round(y, 1), round(x, 2)))
        y += 0.5
    # print only derivative jumps > 0.25mm
    print(f'z={z}')
    prev = None
    for y, x in vals:
        if prev is None or abs(x - prev[1]) > 0.25:
            print(f'   y={y:6.1f} x={x:6.2f}')
        prev = (y, x)
