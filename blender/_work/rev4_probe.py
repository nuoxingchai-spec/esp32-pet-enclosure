import bpy, bmesh, math
from mathutils import Vector

F = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob = bpy.data.objects['Enclosure_Body']
mw = ob.matrix_world
mi = mw.inverted()
dg = bpy.context.evaluated_depsgraph_get()
M3 = mw.to_3x3()
M3i = M3.inverted()

def ray_out(sx, sy, cx, cy, z, th_deg, back=60.0):
    th = math.radians(th_deg)
    ux, uy = sx * math.cos(th), sy * math.sin(th)
    org = mi @ Vector((cx + back * ux, cy + back * uy, z))
    d = (M3i @ Vector((-ux, -uy, 0.0))).normalized()
    ok, loc, nor, idx = ob.ray_cast(org, d, distance=300.0, depsgraph=dg)
    if not ok: return None
    p = mw @ loc
    return dict(x=p.x, y=p.y, z=p.z,
                r=math.hypot(p.x - cx, p.y - cy),
                nx=(M3 @ nor).x, ny=(M3 @ nor).y)

# rear-right corner: C=(30,-55); rays point +x,-y
C = (30.0, -55.0)
print("=== RR OUTER profile r(theta) ===")
print("th   -5    -3     0     3     6    10    15    20    25    30    35    40    45    50    55    60    65    70    75    80    85    90    95")
ZS = [25.0, 40.0, 48.0, 50.0, 52.0, 53.0, 54.0, 54.30, 54.40, 55.0, 56.0, 58.0, 59.5]
for z in ZS:
    row = []
    for th in [-5,-3,0,3,6,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95]:
        h = ray_out(1, -1, C[0], C[1], z, th)
        row.append("  --  " if h is None else f"{h['r']:6.3f}")
    print(f"z{z:6.2f} " + " ".join(row))

print("\n=== RR INNER wall: ray from C outward ===")
def ray_in(sx, sy, cx, cy, z, th_deg):
    th = math.radians(th_deg)
    ux, uy = sx * math.cos(th), sy * math.sin(th)
    org = mi @ Vector((cx, cy, z))
    d = (M3i @ Vector((ux, uy, 0.0))).normalized()
    ok, loc, nor, idx = ob.ray_cast(org, d, distance=60.0, depsgraph=dg)
    if not ok: return None
    p = mw @ loc
    return math.hypot(p.x - cx, p.y - cy)
for z in [48.0, 50.0, 52.0, 54.0, 54.30, 54.40, 55.0, 56.0, 58.0]:
    row = []
    for th in [0,10,20,30,40,45,50,60,70,80,90]:
        r = ray_in(1, -1, C[0], C[1], z, th)
        row.append("  --  " if r is None else f"{r:6.3f}")
    print(f"z{z:6.2f} " + " ".join(row))

print("\n=== symmetry check FR corner C=(30,55) at z54.3/54.4/56 ===")
for z in [54.3, 54.4, 56.0]:
    row = []
    for th in [0,15,30,45,60,75,90]:
        h = ray_out(1, 1, 30.0, 55.0, z, th)
        row.append("  --  " if h is None else f"{h['r']:6.3f}")
    print(f"z{z:6.2f} " + " ".join(row))

print("\n=== z54.35 rim loops (world) ===")
bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(mw)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
zr = [v for v in bm.verts if abs(v.co.z - 54.35) < 0.02]
print('verts at z54.35:', len(zr))
# classify by face adjacency: any face above 54.4 -> upper; any face below 54.3 -> lower
up = set(); lo = set()
for v in zr:
    for f in v.link_faces:
        zs = [x.co.z for x in f.verts]
        if min(zs) > 54.30:
            up.add(v.index)
        if max(zs) < 54.40:
            lo.add(v.index)
print('connected to faces above:', len(up), ' below:', len(lo), ' both/neither:', len(set(v.index for v in zr) - up - lo))
# lower-only and upper-only ranges per side
for label, s in (('LO', lo), ('UP', up)):
    xs = [bm.verts[i].co.x for i in s]; ys = [bm.verts[i].co.y for i in s]
    print(label, 'n', len(s), 'x', round(min(xs), 3), round(max(xs), 3), 'y', round(min(ys), 3), round(max(ys), 3))
# rim faces z54.35 classification
rimf = []
for f in bm.faces:
    zs = [v.co.z for v in f.verts]
    if min(zs) > 54.30 and max(zs) < 54.40 and f.normal.z > 0.9:
        c = f.calc_center_median()
        if abs(c.x) > 38.5 or abs(c.y) > 63.5:
            rimf.append((f, c))
print('rim faces:', len(rimf))
# list side-only y positions and corner bbox
for f, c in rimf:
    if abs(c.y) < 62.0 and c.x < 0:
        pass
sides = [c for f, c in rimf if abs(c.y) < 62.0]
corners = [c for f, c in rimf if abs(c.y) >= 62.0]
print('side slivers', len(sides), 'corner slivers', len(corners))
for f, c in sorted(rimf, key=lambda t: (round(t[1].x), round(t[1].y))):
    if abs(c.y) < 63.0 and c.x > 0:
        vs = [tuple(round(v, 3) for v in (v.co.x, v.co.y, v.co.z)) for v in f.verts]
        print('rimf', len(f.verts), 'area', round(f.calc_area(), 4), 'c', tuple(round(v, 2) for v in c), vs)
bm.free()

print("\n=== top/bottom extents of body ===")
print('dims', tuple(round(v, 3) for v in ob.dimensions))
print('DONE')
