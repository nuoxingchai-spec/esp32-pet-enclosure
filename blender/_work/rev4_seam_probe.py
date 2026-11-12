import bpy, math, os
from mathutils import Vector
ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, r"blender\_work\rev4_stage.blend"))
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world; mi = mw.inverted(); M3 = mw.to_3x3(); M3i = M3.inverted()
dg = bpy.context.evaluated_depsgraph_get()

def hitX(y, z, sign=1):
    org = mi @ Vector((sign * 60.0, y, z))
    d = (M3i @ Vector((-sign, 0, 0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=200.0, depsgraph=dg)
    if not ok: return None
    p = mw @ loc
    return p.x, p.z, tuple(round(v, 3) for v in (M3 @ nor))

def hitY(x, z, sign=-1):
    org = mi @ Vector((x, sign * 80.0, z))
    d = (M3i @ Vector((0, -sign, 0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=200.0, depsgraph=dg)
    if not ok: return None
    p = mw @ loc
    return p.y, p.z, tuple(round(v, 3) for v in (M3 @ nor))

for y in (0.0, -20.0, -30.0, -45.0, -52.0):
    print(f'--- +X side y={y}')
    for z in (54.25, 54.30, 54.34, 54.35, 54.36, 54.40, 54.50, 54.55, 54.56, 54.60, 55.0, 56.0):
        h = hitX(y, z)
        print(f' z{z:6.2f} ' + ('none' if h is None else f'x={h[0]:7.3f} n={h[2]}'))
for x in (0.0, 20.0, -20.0):
    print(f'--- -Y front x={x}')
    for z in (54.25, 54.30, 54.34, 54.35, 54.36, 54.40, 54.50, 54.55, 54.56, 54.60, 55.0, 56.0):
        h = hitY(x, z)
        print(f' z{z:6.2f} ' + ('none' if h is None else f'y={h[0]:7.3f} n={h[2]}'))
print('DONE')
