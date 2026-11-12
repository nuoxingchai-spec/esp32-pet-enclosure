import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)

def bm_world(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    return bm

def audit(o):
    bm = bm_world(o)
    nm = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    bnd = sum(1 for e in bm.edges if len(e.link_faces) < 2)
    zero = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    parent = list(range(len(bm.verts)))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    bm.verts.ensure_lookup_table()
    for e in bm.edges:
        a, b = find(e.verts[0].index), find(e.verts[1].index)
        if a != b: parent[a] = b
    comps = len({find(i) for i in range(len(bm.verts))})
    vol = bm.calc_volume(signed=True)
    bm.free()
    b = [o.matrix_world @ Vector(c) for c in o.bound_box]
    xs = [p.x for p in b]; ys = [p.y for p in b]; zs = [p.z for p in b]
    print(f"AUDIT {o.name:20s} v={len(o.data.vertices):5d} f={len(o.data.polygons):5d} nm={nm:3d} bnd={bnd:3d}"
          f" zero={zero:3d} comps={comps:2d} vol={vol:9.1f}"
          f"  dim {o.dimensions.x:7.2f}x{o.dimensions.y:7.2f}x{o.dimensions.z:7.2f}"
          f"  z[{min(zs):6.2f},{max(zs):6.2f}]")

def bvh(o):
    bm = bm_world(o); t = BVHTree.FromBMesh(bm); bm.free(); return t

def overlap(a, b, label):
    ta, tb = bvh(a), bvh(b)
    pairs = ta.overlap(tb)
    if pairs:
        print(f"OVERLAP {label:34s} faces={len(pairs):5d}")
    else:
        print(f"OK      {label:34s} no face overlap")

def mindist(a, b, label, step=1):
    tb = bvh(b)
    bm = bm_world(a); bm.verts.ensure_lookup_table()
    best = 1e9; bp = None
    for i in range(0, len(bm.verts), step):
        p = bm.verts[i].co
        loc, nor, idx, d = tb.find_nearest(p)
        if loc is not None and d < best:
            best = d; bp = loc
    bm.free()
    print(f"DIST    {label:34s} min={best:.3f}")

PRINT = ['Enclosure_Body','Enclosure_Lid','Face_Plate','Belly_Pan','LED_Diffuser_Ring',
         'Leg_R','Leg_R_Rear','Leg_L','Leg_L_Rear','Button_Top_1','Button_Top_2','Button_Top_3',
         'Ear_R','Ear_L','Tail']
print("=== PRINT PART AUDIT ===")
for n in PRINT:
    o = bpy.data.objects.get(n)
    if o: audit(o)
    else: print('MISSING', n)

print("\n=== SEAM FLUSH (world z 54.20 vs 54.55) ===")
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world; mi = mw.inverted(); M3i = mw.to_3x3().inverted()
dg = bpy.context.evaluated_depsgraph_get()
def cast(sx, y, z):
    org = mi @ Vector((sx * 60.0, y, z))
    d = (M3i @ Vector((-sx, 0.0, 0.0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=200.0, depsgraph=dg)
    if not ok: return None
    return (mw @ loc).x * sx
worst = 0.0
for sx in (1, -1):
    for y in (30.0, 35.3, 45.0, -30.0, -35.3, -45.0):
        lo = cast(sx, y, 54.20); up = cast(sx, y, 54.55)
        d = (lo - up) * 1000.0
        worst = max(worst, abs(d))
        print(f"  sx={sx:+d} y={y:6.1f} lo={lo:.5f} up={up:.5f} d={d:6.2f}um")
print(f"SEAM-WORST {worst:.2f}um")

print("\n=== OVERLAP CHECKS ===")
pairs = [
 ('Button_Top_1','Enclosure_Lid'),('Button_Top_2','Enclosure_Lid'),('Button_Top_3','Enclosure_Lid'),
 ('Button_Top_1','PCB_Board'),('Button_Top_2','PCB_Board'),('Button_Top_3','PCB_Board'),
 ('Button_Top_1','PCB_Components'),('Button_Top_2','PCB_Components'),('Button_Top_3','PCB_Components'),
 ('Button_Top_1','LED_Diffuser_Ring'),('Button_Top_2','LED_Diffuser_Ring'),('Button_Top_3','LED_Diffuser_Ring'),
 ('Ear_R','Enclosure_Lid'),('Ear_L','Enclosure_Lid'),('Tail','Enclosure_Lid'),
 ('Ear_R','LED_Diffuser_Ring'),('Ear_L','LED_Diffuser_Ring'),('Tail','LED_Diffuser_Ring'),
 ('Ear_R','Touch_Module_Fit'),('Ear_L','Touch_Module_Fit'),('Tail','Touch_Module_Fit'),
 ('Ear_R','Enclosure_Body'),('Ear_L','Enclosure_Body'),('Tail','Enclosure_Body'),
 ('Touch_Module_Fit','Enclosure_Lid'),
 ('Button_Top_1','Battery_103450'),('Button_Top_2','Battery_103450'),('Button_Top_3','Battery_103450'),
 ('Tail','Battery_103450'),
]
bad = 0
for a, b in pairs:
    oa, ob = bpy.data.objects.get(a), bpy.data.objects.get(b)
    if not oa or not ob:
        print('SKIP', a, b); continue
    ta, tb = bvh(oa), bvh(ob)
    n = len(ta.overlap(tb))
    if n: bad += 1
    print(f"{'OVERLAP' if n else 'OK     '} {a+' x '+b:34s} faces={n}")
print(f"PAIRS {len(pairs)}  BAD {bad}")

print("\n=== CLEARANCES ===")
pairs2 = [
 ('Ear_R','LED_Diffuser_Ring',1),('Ear_L','LED_Diffuser_Ring',1),('Tail','LED_Diffuser_Ring',1),
 ('Tail','Enclosure_Body',2),('Ear_R','Touch_Module_Fit',2),('Ear_L','Touch_Module_Fit',2),
 ('Touch_Module_Fit','Enclosure_Lid',1),
 ('Button_Top_1','PCB_Components',1),('Button_Top_2','PCB_Components',1),('Button_Top_3','PCB_Components',1),
]
for a, b, s in pairs2:
    oa, ob = bpy.data.objects.get(a), bpy.data.objects.get(b)
    if oa and ob: mindist(oa, ob, f'{a} -> {b}', s)

print("\n=== OVERALL ===")
xs=[]; ys=[]; zs=[]
for o in bpy.context.scene.objects:
    if o.type != 'MESH' or o.hide_viewport: continue
    for c in o.bound_box:
        p = o.matrix_world @ Vector(c); xs.append(p.x); ys.append(p.y); zs.append(p.z)
print(f"visible bbox x[{min(xs):.2f},{max(xs):.2f}] y[{min(ys):.2f},{max(ys):.2f}] z[{min(zs):.2f},{max(zs):.2f}]"
      f"  size {max(xs)-min(xs):.2f} x {max(ys)-min(ys):.2f} x {max(zs)-min(zs):.2f}")
print('DONE')
