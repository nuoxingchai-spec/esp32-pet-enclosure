import bpy, math
from mathutils import Vector

BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)

def clusters(pts, tol=0.45):
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

def rings2d(pts, label, minn=8, maxdev=0.12, maxr=3.0):
    for g in clusters([Vector((p[0], p[1], 0)) for p in pts]):
        if len(g) < minn: continue
        cx = sum(p.x for p in g)/len(g); cy = sum(p.y for p in g)/len(g)
        rs = [math.hypot(p.x-cx, p.y-cy) for p in g]
        r = sum(rs)/len(rs); dev = max(abs(v-r) for v in rs)
        if dev < maxdev and r < maxr:
            print(f"    {label}: c=({cx:.3f},{cy:.3f}) r={r:.3f} n={len(g)} dev={dev:.3f}")

def slice_plane(obj, axis, val, tol=0.02):
    o = bpy.data.objects[obj]
    pts = []
    for v in o.data.vertices:
        p = o.matrix_world @ v.co
        if abs(getattr(p, axis) - val) < tol:
            pts.append((p.x, p.y, p.z))
    return pts

print("### FACE PLATE: outer face y=64.05 (x,z rings)")
rings2d([(p[0], p[2]) for p in slice_plane('Face_Plate','y',64.05)], 'outer')
print("### FACE PLATE: back face y=61.85")
rings2d([(p[0], p[2]) for p in slice_plane('Face_Plate','y',61.85)], 'back')
for yv in (63.9, 63.4, 63.0, 62.5, 62.0):
    print(f"### FACE PLATE y={yv}")
    rings2d([(p[0], p[2]) for p in slice_plane('Face_Plate','y',yv)], f'y{yv}')

print("### BODY: y=64.0 (front outer)")
rings2d([(p[0], p[2]) for p in slice_plane('Enclosure_Body','y',64.0)], 'front64', maxr=6)
for yv in (63.5, 63.0, 62.5, 62.0, 61.9):
    print(f"### BODY y={yv}")
    rings2d([(p[0], p[2]) for p in slice_plane('Enclosure_Body','y',yv)], f'y{yv}', maxr=6)

# body bottom bosses: vertical holes near x=+-20, y in (30,-50,48)
print("### BODY bottom hole columns")
o = bpy.data.objects['Enclosure_Body']
centers = [(20,30),(-20,30),(20,-50),(-20,-50),(20,48),(-20,48)]
for (cx, cy) in centers:
    zs = {}
    for v in o.data.vertices:
        p = o.matrix_world @ v.co
        if math.hypot(p.x-cx, p.y-cy) < 2.6 and p.z < 30:
            zs.setdefault(round(p.z,2), []).append(math.hypot(p.x-cx, p.y-cy))
    print(f"  boss ({cx},{cy}):")
    for z in sorted(zs):
        rs = zs[z]
        print(f"    z={z:.2f} n={len(rs)} rmin={min(rs):.3f} rmax={max(rs):.3f}")

# belly pan holes: bottom/top planes; check actual z values
o = bpy.data.objects['Belly_Pan']
zs = sorted({round((o.matrix_world @ v.co).z, 2) for v in o.data.vertices})
print("### Belly_Pan z levels:", zs)
for z in (17.2, 19.7):
    print(f"  z={z}")
    rings2d([( (o.matrix_world@v.co).x, (o.matrix_world@v.co).y) for v in o.data.vertices
             if abs((o.matrix_world@v.co).z - z) < 0.02], f'z{z}', minn=6, maxdev=0.2)
