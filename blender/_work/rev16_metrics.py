import bpy, bmesh
from mathutils.bvhtree import BVHTree
BLEND = r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend'
bpy.ops.wm.open_mainfile(filepath=BLEND)
sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()

def ev(n):
    o = bpy.data.objects[n].evaluated_get(dg)
    m = o.to_mesh()
    return o, m, o.matrix_world

def world_bbox(n):
    o, m, mw = ev(n)
    vs = [mw @ v.co for v in m.vertices]
    return (min(v.x for v in vs), max(v.x for v in vs), min(v.y for v in vs), max(v.y for v in vs), min(v.z for v in vs), max(v.z for v in vs))

print('=== PRINTED PART BBOX (world mm) ===')
names = [o.name for o in bpy.data.collections['RobotDog_v3'].objects if o.type == 'MESH']
allv = []
for n in sorted(names):
    b = world_bbox(n)
    print('BBOX', n, ' '.join(f'{v:.2f}' for v in b), 'size', f'{b[1]-b[0]:.2f}x{b[3]-b[2]:.2f}x{b[5]-b[4]:.2f}')
    o, m, mw = ev(n)
    allv += [mw @ v.co for v in m.vertices]
print('ASSEMBLY', f'{min(v.x for v in allv):.2f}..{max(v.x for v in allv):.2f}',
      f'{min(v.y for v in allv):.2f}..{max(v.y for v in allv):.2f}',
      f'{min(v.z for v in allv):.2f}..{max(v.z for v in allv):.2f}',
      'size', f'{max(v.x for v in allv)-min(v.x for v in allv):.2f}x{max(v.y for v in allv)-min(v.y for v in allv):.2f}x{max(v.z for v in allv)-min(v.z for v in allv):.2f}')

def inter(a, b):
    A = bpy.data.objects[a]; B = bpy.data.objects[b]
    da = A.copy(); da.data = A.data.copy(); sc.collection.objects.link(da)
    db = B.copy(); db.data = B.data.copy(); sc.collection.objects.link(db)
    for m in list(da.modifiers): da.modifiers.remove(m)
    for m in list(db.modifiers): db.modifiers.remove(m)
    bpy.context.view_layer.objects.active = da
    md = da.modifiers.new('i', 'BOOLEAN'); md.operation = 'INTERSECT'; md.solver = 'EXACT'; md.object = db
    bpy.ops.object.modifier_apply(modifier=md.name)
    bm = bmesh.new(); bm.from_mesh(da.data)
    vol = bm.calc_volume(signed=True) if bm.faces else 0
    print('INTERSECT', a, 'x', b, 'vol', f'{vol:.4f}', 'faces', len(bm.faces))
    bm.free()
    bpy.data.objects.remove(da, do_unlink=True); bpy.data.objects.remove(db, do_unlink=True)

print('=== EXACT BOOLEAN INTERSECTIONS (mm3) ===')
for a, b in [('Enclosure_Lid', 'Enclosure_Body'), ('Face_Plate', 'Enclosure_Body'), ('Belly_Pan', 'Enclosure_Body'),
             ('LED_Diffuser_Ring', 'Enclosure_Lid'), ('Tail', 'Enclosure_Lid'), ('Ear_R', 'Enclosure_Lid'),
             ('Ear_L', 'Enclosure_Lid'), ('Button_Top_1', 'Enclosure_Lid'), ('Button_Top_2', 'Enclosure_Lid'),
             ('Button_Top_3', 'Enclosure_Lid'), ('Touch_Module_Fit', 'Enclosure_Lid'),
             ('PCB_Board', 'Enclosure_Body'), ('Battery_103450', 'Enclosure_Body'),
             ('Speaker_3070', 'Enclosure_Body')]:
    inter(a, b)

def mindist(a, b):
    oa, ma, mwa = ev(a); ob, mb, mwb = ev(b)
    va = [mwa @ v.co for v in ma.vertices]; vb = [mwb @ v.co for v in mb.vertices]
    ta = BVHTree.FromPolygons(va, [p.vertices[:] for p in ma.polygons], epsilon=0.0)
    tb = BVHTree.FromPolygons(vb, [p.vertices[:] for p in mb.polygons], epsilon=0.0)
    best = 1e9
    for v in va:
        loc, nor, idx, d = tb.find_nearest(v, 1000.0)
        if loc is not None: best = min(best, d)
    for v in vb:
        loc, nor, idx, d = ta.find_nearest(v, 1000.0)
        if loc is not None: best = min(best, d)
    return best

print('=== SURFACE DISTANCES (mm) ===')
for a, b in [('Tail', 'LED_Diffuser_Ring'), ('Tail', 'Enclosure_Body'), ('Ear_R', 'LED_Diffuser_Ring'),
             ('Ear_L', 'LED_Diffuser_Ring'), ('Ear_R', 'Touch_Module_Fit'), ('Ear_L', 'Touch_Module_Fit'),
             ('Touch_Module_Fit', 'Enclosure_Lid'), ('Button_Top_2', 'PCB_Components'),
             ('Enclosure_Lid', 'Enclosure_Body'), ('Face_Plate', 'OLED_1p3_Module'),
             ('Tail', 'Touch_Module_Fit'), ('Belly_Pan', 'Battery_103450')]:
    print('DIST', a, b, f'{mindist(a, b):.4f}')
