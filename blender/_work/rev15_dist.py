import bpy, bmesh, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BLEND = r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend'
bpy.ops.wm.open_mainfile(filepath=BLEND)
dg = bpy.context.evaluated_depsgraph_get()
def ev(n):
    o = bpy.data.objects[n].evaluated_get(dg)
    m = o.to_mesh()
    mw = o.matrix_world
    return o, m, mw
def world_bbox(n):
    o, m, mw = ev(n)
    vs = [mw @ v.co for v in m.vertices]
    return (min(v.x for v in vs), max(v.x for v in vs), min(v.y for v in vs), max(v.y for v in vs), min(v.z for v in vs), max(v.z for v in vs))
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
for n in ['Tail', 'LED_Diffuser_Ring', 'Ear_R', 'Ear_L', 'Touch_Module_Fit', 'Button_Top_2', 'Enclosure_Lid', 'Enclosure_Body']:
    print('BBOX', n, tuple(round(v, 2) for v in world_bbox(n)))
for a, b in [('Tail', 'LED_Diffuser_Ring'), ('Tail', 'Enclosure_Body'), ('Ear_R', 'LED_Diffuser_Ring'),
             ('Ear_L', 'LED_Diffuser_Ring'), ('Touch_Module_Fit', 'Enclosure_Lid'),
             ('Button_Top_2', 'PCB_Components'), ('Enclosure_Lid', 'Enclosure_Body'),
             ('Face_Plate', 'OLED_1p3_Module')]:
    print('DIST', a, b, round(mindist(a, b), 4))
