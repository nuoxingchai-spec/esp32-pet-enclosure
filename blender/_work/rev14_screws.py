import bpy, bmesh, math
from mathutils import Vector
from collections import defaultdict

BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)

def clusters_xy(pts, tol=0.4):
    pts = list(pts); out = []
    while pts:
        seed = pts.pop(); grp = [seed]; changed = True
        while changed:
            changed = False
            for p in pts[:]:
                if any((p-q).length < tol for q in grp):
                    grp.append(p); pts.remove(p); changed = True
        out.append(grp)
    return out

def ring_info(grp):
    cx = sum(p.x for p in grp)/len(grp); cy = sum(p.y for p in grp)/len(grp)
    rs = [(p.x-cx)**2 + (p.y-cy)**2 for p in grp]
    r = math.sqrt(sum(rs)/len(rs))
    dev = max(abs(math.sqrt(v)-r) for v in rs)
    return cx, cy, r, len(grp), dev

def zrings(obj, z, tol=0.02):
    o = bpy.data.objects[obj]
    pts = [o.matrix_world @ v.co for v in o.data.vertices if abs((o.matrix_world @ v.co).z - z) < tol]
    print(f"--- {obj} z={z} verts={len(pts)}")
    for g in clusters_xy(pts):
        if len(g) >= 8:
            cx, cy, r, n, dev = ring_info(g)
            print(f"    c=({cx:.3f},{cy:.3f}) r={r:.3f} n={n} dev={dev:.3f}")

for z in (17.2, 19.7):
    zrings('Belly_Pan', z)
for z in (19.7, 20.0):
    zrings('Enclosure_Body', z)
zrings('Face_Plate', 64.05)
zrings('Face_Plate', 61.85)
zrings('Enclosure_Body', 61.85)
# legs: hole in outer x face and inner
for obj in ('Leg_R',):
    o = bpy.data.objects[obj]
    for x in (40.0, 48.0):
        pts = [o.matrix_world @ v.co for v in o.data.vertices if abs((o.matrix_world @ v.co).x - x) < 0.02]
        print(f"--- {obj} x={x} verts={len(pts)}")
        for g in clusters_xy([Vector((p.y, p.z, 0)) for p in pts]):
            if len(g) >= 8:
                cx, cy, r, n, dev = ring_info(g)
                print(f"    c=({cx:.3f},{cy:.3f}) r={r:.3f} n={n} dev={dev:.3f}")
