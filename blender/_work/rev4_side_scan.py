import bpy, math
from mathutils import Vector
F = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world; mi = mw.inverted(); M3 = mw.to_3x3(); M3i = M3.inverted()
dg = bpy.context.evaluated_depsgraph_get()
def hit(sx, y, z):
    org = mi @ Vector((sx * 60.0, y, z))
    d = (M3i @ Vector((-sx, 0, 0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=200.0, depsgraph=dg)
    if not ok: return None
    p = mw @ loc
    return abs(p.x), tuple(round(v, 2) for v in (M3 @ nor))
for z in (54.5, 55.0, 56.0, 57.0, 58.0):
    print('=== z', z, '+X side')
    for y in range(-56, 57, 2):
        h = hit(1, y, z)
        print(f' y{y:4d} ' + ('none' if h is None else f'x={h[0]:7.3f} n={h[1]}'))
print('DONE')
