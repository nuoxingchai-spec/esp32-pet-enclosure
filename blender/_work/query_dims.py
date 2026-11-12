import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

bpy.ops.wm.open_mainfile(filepath=r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage3.blend')

def wb(o):
    return [o.matrix_world @ Vector(c) for c in o.bound_box]

for n in ['Enclosure_Body', 'Enclosure_Lid', 'Face_Plate', 'Belly_Pan', 'LED_Diffuser_Ring',
          'OLED_1p3_Module', 'OLED_ActiveArea', 'Leg_R', 'Leg_R_Rear', 'Leg_L', 'Leg_L_Rear',
          'SG90_Fit_1', 'PCB_Board', 'PCB_Components', 'Battery_103450', 'Speaker_3070',
          'Touch_Module_Fit', 'Button_Plunger_1']:
    o = bpy.data.objects.get(n)
    if not o:
        print('MISSING', n)
        continue
    b = wb(o)
    xs = [p.x for p in b]; ys = [p.y for p in b]; zs = [p.z for p in b]
    print(f'{n:22s} dim {o.dimensions.x:7.3f} {o.dimensions.y:7.3f} {o.dimensions.z:7.3f}'
          f'  x[{min(xs):7.2f},{max(xs):7.2f}] y[{min(ys):7.2f},{max(ys):7.2f}] z[{min(zs):6.2f},{max(zs):6.2f}]')

body = bpy.data.objects['Enclosure_Body']
bm = bmesh.new(); bm.from_mesh(body.data); bm.transform(body.matrix_world)
bvh = BVHTree.FromBMesh(bm)

def scan(label, origin_axis, fixed, u_range, v_range, step=0.25):
    hits = []
    u0, u1 = u_range; v0, v1 = v_range
    u = u0
    while u <= u1:
        v = v0
        while v <= v1:
            if fixed == '+X':
                org = Vector((60, u, v)); d = Vector((-1, 0, 0))
            elif fixed == '-X':
                org = Vector((-60, u, v)); d = Vector((1, 0, 0))
            elif fixed == '+Y':
                org = Vector((u, 80, v)); d = Vector((0, -1, 0))
            elif fixed == '-Y':
                org = Vector((u, -80, v)); d = Vector((0, 1, 0))
            loc, nor, idx, dist = bvh.ray_cast(org, d, 200)
            if loc is not None:
                if fixed == '+X':
                    open_ = loc.x < 30
                elif fixed == '-X':
                    open_ = loc.x > -30
                elif fixed == '+Y':
                    open_ = loc.y < 55
                else:
                    open_ = loc.y > -55
                if open_:
                    hits.append((u, v))
            v += step
        u += step
    # cluster
    clusters = []
    for (u, v) in hits:
        placed = False
        for c in clusters:
            if c['u0'] - step <= u <= c['u1'] + step and c['v0'] - step <= v <= c['v1'] + step:
                c['u0'] = min(c['u0'], u); c['u1'] = max(c['u1'], u)
                c['v0'] = min(c['v0'], v); c['v1'] = max(c['v1'], v)
                placed = True; break
        if not placed:
            clusters.append({'u0': u, 'u1': u, 'v0': v, 'v1': v})
    merged = True
    while merged:
        merged = False
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                a, b = clusters[i], clusters[j]
                if not (a['u1'] + step < b['u0'] or b['u1'] + step < a['u0'] or
                        a['v1'] + step < b['v0'] or b['v1'] + step < a['v0']):
                    a['u0'] = min(a['u0'], b['u0']); a['u1'] = max(a['u1'], b['u1'])
                    a['v0'] = min(a['v0'], b['v0']); a['v1'] = max(a['v1'], b['v1'])
                    clusters.pop(j); merged = True; break
            if merged:
                break
    print('WALL', label)
    for c in sorted(clusters, key=lambda c: -c['v1']):
        print(f"   u {c['u0']:.2f}..{c['u1']:.2f}  v {c['v0']:.2f}..{c['v1']:.2f}  size {c['u1']-c['u0']:.2f} x {c['v1']-c['v0']:.2f}")

# +X wall: u=y, v=z
scan('+X (SD)', '+X', '+X', (-64, 64), (60, 66), 0.2)
scan('+X full', '+X', '+X', (-64, 64), (22, 66), 0.3)
scan('-X (buttons)', '-X', '-X', (-64, 64), (48, 60), 0.2)
scan('-Y (USB/switch)', '-Y', '-Y', (-40, 40), (48, 60), 0.2)
scan('+Y rear', '+Y', '+Y', (-40, 40), (48, 60), 0.3)
bm.free()
print('DONE')
