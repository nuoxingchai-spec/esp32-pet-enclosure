import bpy, math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev6_corner.blend")
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world; mi = mw.inverted()
M3i = mw.to_3x3().inverted()
dg = bpy.context.evaluated_depsgraph_get()
def ray_r(cx, cy, sx, sy, z, th_deg, back=60.0):
    a = math.radians(th_deg)
    ux, uy = sx * math.cos(a), sy * math.sin(a)
    org = mi @ Vector((cx + back * ux, cy + back * uy, z))
    d = (M3i @ Vector((-ux, -uy, 0.0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=300.0, depsgraph=dg)
    if not ok: return None
    p = mw @ loc
    return (math.hypot(p.x - cx, p.y - cy), p.x, p.y)
for cname, cx, cy, sx, sy in [('FR', 30, -55, 1, -1), ('FL', -30, -55, -1, -1), ('RR', 30, 55, 1, 1), ('RL', -30, 55, -1, 1)]:
    print("CORNER", cname)
    for th in range(-15, 66, 5):
        lo = ray_r(cx, cy, sx, sy, 54.30, th)
        hi = ray_r(cx, cy, sx, sy, 54.40, th)
        print("  th=%3d lo=%s hi=%s d=%s" % (th,
              ("%.4f(%.2f,%.2f)" % lo) if lo else None,
              ("%.4f(%.2f,%.2f)" % hi) if hi else None,
              ("%.4f" % (lo[0] - hi[0])) if lo and hi else None))
print("SIDE +X fine profile")
for i in range(0, 61, 2):
    y = 27.0 + i
    vals = []
    for z in (54.28, 54.32, 54.38, 54.44):
        org = mi @ Vector((60, y, z))
        d = (M3i @ Vector((-1, 0, 0))).normalized()
        ok, loc, nor, idx = body.ray_cast(org, d, distance=60, depsgraph=dg)
        vals.append(round((mw @ loc).x, 4) if ok else None)
    print("  y=%5.1f %s d=%.4f" % (y, vals, (vals[1] - vals[2]) if all(vals) else 0))
