import bpy, bmesh, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage5b.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)

def act(o):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o

def bm_world(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    return bm

def audit(o):
    bm = bm_world(o)
    nm = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    bnd = sum(1 for e in bm.edges if len(e.link_faces) < 2)
    # components via union-find
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
    print(f"AUDIT {o.name:20s} v={len(o.data.vertices):5d} f={len(o.data.polygons):5d} nm={nm:3d} bnd={bnd:3d} comps={comps:2d} vol={vol:9.1f}"
          f"  dim {o.dimensions.x:7.2f}x{o.dimensions.y:7.2f}x{o.dimensions.z:7.2f}"
          f"  x[{min(xs):7.2f},{max(xs):7.2f}] y[{min(ys):7.2f},{max(ys):7.2f}] z[{min(zs):6.2f},{max(zs):6.2f}]")
    return nm, comps

def bvh(o):
    bm = bm_world(o); t = BVHTree.FromBMesh(bm); bm.free(); return t

def overlap(a, b, label):
    va = set(); 
    ta, tb = bvh(a), bvh(b)
    pairs = ta.overlap(tb)
    if pairs:
        # collect overlapping points roughly
        pts = []
        bm = bm_world(a); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
        for ia, ib in pairs[:20]:
            f = bm.faces[ia] if ia < len(bm.faces) else None
            if f: pts.append(tuple(round(v,1) for v in f.calc_center_median()))
        bm.free()
        print(f"OVERLAP {label:34s} faces={len(pairs):5d} e.g. {pts[:6]}")
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
    print(f"DIST    {label:34s} min={best:.3f} at {tuple(round(v,1) for v in bp) if bp else None}")

PRINT = ['Enclosure_Body','Enclosure_Lid','Face_Plate','Belly_Pan','LED_Diffuser_Ring',
         'Leg_R','Leg_R_Rear','Leg_L','Leg_L_Rear','Button_Top_1','Button_Top_2','Button_Top_3',
         'Ear_R','Ear_L','Tail']
print("=== PRINT PART AUDIT ===")
for n in PRINT:
    o = bpy.data.objects.get(n)
    if o: audit(o)
    else: print('MISSING', n)

print("\n=== ALL OBJECTS ===")
for o in bpy.context.scene.objects:
    if o.type != 'MESH': continue
    b = [o.matrix_world @ Vector(c) for c in o.bound_box]
    xs=[p.x for p in b]; ys=[p.y for p in b]; zs=[p.z for p in b]
    print(f"{o.name:24s} vis={int(not o.hide_viewport)}  x[{min(xs):7.2f},{max(xs):7.2f}] y[{min(ys):7.2f},{max(ys):7.2f}] z[{min(zs):6.2f},{max(zs):6.2f}]")

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
for a,b in pairs:
    oa, ob = bpy.data.objects.get(a), bpy.data.objects.get(b)
    if not oa or not ob:
        print('SKIP', a, b); continue
    overlap(oa, ob, f'{a} x {b}')

print("\n=== CLEARANCES ===")
pairs2 = [
 ('Ear_R','LED_Diffuser_Ring',1),('Ear_L','LED_Diffuser_Ring',1),('Tail','LED_Diffuser_Ring',1),
 ('Tail','Enclosure_Body',2),('Ear_R','Touch_Module_Fit',2),('Ear_L','Touch_Module_Fit',2),
 ('Touch_Module_Fit','Enclosure_Lid',1),
 ('Button_Top_1','PCB_Components',1),('Button_Top_2','PCB_Components',1),('Button_Top_3','PCB_Components',1),
]
for a,b,s in pairs2:
    oa, ob = bpy.data.objects.get(a), bpy.data.objects.get(b)
    if oa and ob: mindist(oa, ob, f'{a} -> {b}', s)

# overall visible (non-master) bbox
print("\n=== OVERALL ===")
xs=[];ys=[];zs=[]
for o in bpy.context.scene.objects:
    if o.type != 'MESH' or o.hide_viewport: continue
    for c in o.bound_box:
        p=o.matrix_world @ Vector(c); xs.append(p.x);ys.append(p.y);zs.append(p.z)
print(f"visible bbox x[{min(xs):.2f},{max(xs):.2f}] y[{min(ys):.2f},{max(ys):.2f}] z[{min(zs):.2f},{max(zs):.2f}]"
      f"  size {max(xs)-min(xs):.2f} x {max(ys)-min(ys):.2f} x {max(zs)-min(zs):.2f}")

# touch module exact bbox + lid ceiling probes
tm = bpy.data.objects.get('Touch_Module_Fit')
if tm:
    print('TOUCH loc', tuple(round(v,3) for v in tm.location))
lid = bpy.data.objects['Enclosure_Lid']; tl = bvh(lid)
for x in (-3.2,0,3.2):
    for y in (35,):
        loc,nor,idx,d = tl.ray_cast(Vector((x,y,80)), Vector((0,0,-1)), 100)
        print(f"SLIT ray x{x} y{y}: first hit z={loc.z:.3f}" if loc else "no hit")
# ceiling underside near ear slot / tail slot / touch module
for (x,y,lab) in [(0,35,'touch'),(0,47,'touch-front'),(21,30,'earR'),(0,-46,'tail'),(-24.83,-42.45,'btn2'),(0,0,'center')]:
    loc,nor,idx,d = tl.ray_cast(Vector((x,y,50)), Vector((0,0,1)), 100)
    print(f"CEIL up {lab:10s} ({x},{y}) first hit z={loc.z:.3f}" if loc else f"CEIL up {lab} no hit")
# button cap/seat: downward ray at button center, and at offset x+2.25
for y in (-35.47,-42.45,-49.47):
    for dx in (0.0, 2.25, 2.6):
        loc,nor,idx,d = tl.ray_cast(Vector((-24.83+dx,y,80)), Vector((0,0,-1)), 100)
        print(f"BTN ray dx={dx:4.2f} y={y:.2f}: hit z={loc.z:.3f}" if loc else f"BTN ray dx={dx} y={y} no hit")
print('DONE')
