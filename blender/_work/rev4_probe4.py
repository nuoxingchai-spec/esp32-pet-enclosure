import bpy, math
from mathutils import Vector
F = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
sc = bpy.context.scene
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world; mi = mw.inverted(); M3 = mw.to_3x3(); M3i = M3.inverted()
dg = bpy.context.evaluated_depsgraph_get()
print('MW')
for r in mw: print(' ', [round(v,4) for v in r])
print('dims', tuple(round(v,3) for v in body.dimensions))
print('loc', tuple(round(v,3) for v in body.location))
print('hidden', body.hide_viewport, body.hide_render, body.hide_get())

CORNERS = {'FR': (30.0, -55.0, 1, -1), 'FL': (-30.0, -55.0, -1, -1),
           'RR': (30.0, 55.0, 1, 1),  'RL': (-30.0, 55.0, -1, 1)}

def ray_r(cx, cy, z, th_deg, back=60.0):
    th = math.radians(th_deg)
    ux, uy = math.cos(th), -math.sin(th)
    org = mi @ Vector((cx + back*ux, cy + back*uy, z))
    d = (M3i @ Vector((-ux, -uy, 0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=300.0, depsgraph=dg)
    if not ok: return None
    p = mw @ loc
    return math.hypot(p.x-cx, p.y-cy), (M3 @ nor).x, (M3 @ nor).y, p.z

for tag,(cx,cy,sx,sy) in CORNERS.items():
    print('=== corner', tag, cx, cy)
    for z in (50.0, 52.0, 53.0, 54.0, 54.34, 54.36, 55.0, 56.0, 58.0):
        diffs=[]; bad=[]
        for i in range(0,91,1):
            a = math.radians(i)
            # map local corner angle to world direction using signs
            ux, uy = sx*math.cos(a), sy*math.sin(a)
            org = mi @ Vector((cx + 60*ux, cy + 60*uy, z))
            d = (M3i @ Vector((-ux, -uy, 0))).normalized()
            ok, loc, nor, idx = body.ray_cast(org, d, distance=300.0, depsgraph=dg)
            if not ok: bad.append(i); continue
            p = mw @ loc
            diffs.append((i, math.hypot(p.x-cx,p.y-cy), p.z))
        if z == 54.34: ref = diffs
        rs = [d[1] for d in diffs]
        print(f' z{z:6.2f} n={len(diffs)} bad={len(bad)} rmin={min(rs):.4f} rmax={max(rs):.4f}')
    # profile tables lower/upper
    print(' th  rL(z52)  rU(z56)  step')
    for i in range(0,91,5):
        a = math.radians(i); ux, uy = sx*math.cos(a), sy*math.sin(a)
        def rr(z):
            org = mi @ Vector((cx + 60*ux, cy + 60*uy, z))
            d = (M3i @ Vector((-ux, -uy, 0))).normalized()
            ok, loc, nor, idx = body.ray_cast(org, d, distance=300.0, depsgraph=dg)
            p = mw @ loc
            return math.hypot(p.x-cx,p.y-cy)
        rl, ru = rr(52.0), rr(56.0)
        print(f' {i:3d} {rl:8.4f} {ru:8.4f} {rl-ru:7.4f}')
print('DONE')
