import bpy
from mathutils.bvhtree import BVHTree
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)

def bvh(o):
    m = o.matrix_world
    vs = [m @ v.co for v in o.data.vertices]
    fs = [tuple(p.vertices) for p in o.data.polygons]
    return BVHTree.FromPolygons(vs, fs, all_triangles=False)

body = bpy.data.objects['Enclosure_Body']
sg = bpy.data.objects['SG90_Fit_1']
tb, ts = bvh(body), bvh(sg)
pairs = tb.overlap(ts)
print('pairs', len(pairs))
from collections import Counter
c = Counter()
pts = []
for (i, j) in pairs:
    p = body.data.polygons[i]
    ctr = body.matrix_world @ p.center
    c[(round(ctr.x,1), round(ctr.y,1), round(ctr.z,1))] += 1
    pts.append(ctr)
print('unique body face centers', len(c))
for k, n in c.most_common(30):
    print(' ', k, n)
# bbox of overlapping body faces
if pts:
    print('overlap bbox', tuple(round(min(p[i] for p in pts),2) for i in range(3)),
          tuple(round(max(p[i] for p in pts),2) for i in range(3)))
# servo mesh bbox in local/world
print('servo world bbox', tuple(round(v,2) for v in sg.dimensions))
# body bay: raycast from servo center outward in X, Y, Z
def wr(obj, origin, direction):
    mw = obj.matrix_world; inv = mw.inverted()
    hit, loc, nor, idx = obj.ray_cast(inv @ origin, (inv.to_3x3() @ direction).normalized(), distance=500)
    return None if not hit else (mw @ loc, (mw.to_3x3().inverted().transposed() @ nor).normalized())
for d, lab in [((0,0,-1),'down'),((0,0,1),'up'),((0,1,0),'inY'),((0,-1,0),'outY'),((-1,0,0),'inX'),((1,0,0),'outX')]:
    r = wr(body, (28.4,44,38), d)
    print(lab, None if not r else (round((r[0]).x,2), round((r[0]).y,2), round((r[0]).z,2)))
