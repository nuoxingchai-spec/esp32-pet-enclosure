import bpy, math, os
from mathutils import Vector

ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, r"blender\robot_dog_enclosure_v3.blend"))
sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()

print("=== BUTTON OBJECTS ===")
for o in sorted(sc.objects, key=lambda x: x.name):
    if 'Button' in o.name:
        print(f"  {o.name:24s} type={o.type} mesh={o.data.name if o.type=='MESH' else '-'} "
              f"loc={tuple(round(v,3) for v in o.location)} users={o.data.users if o.type=='MESH' else 0}")
        print(f"      dims={tuple(round(v,3) for v in o.dimensions)} hide_viewport={o.hide_viewport}")

btn = bpy.data.objects['Button_Top_1']
mw = btn.matrix_world
mi = mw.inverted(); M3i = mw.to_3x3().inverted()
print("BTN matrix_world=", [round(v,4) for r in mw for v in r])
print("BTN bbox local:", [round(v,4) for v in btn.bound_box[0]], [round(v,4) for v in btn.bound_box[6]])
print("BTN verts", len(btn.data.vertices), "faces", len(btn.data.polygons))

def bcast(sx, sy, r0, z, ang, dist=30.0):
    # cast from outside toward the local axis at height z, angle ang (deg, x=cos, y=sin)
    a = math.radians(ang)
    d = Vector((-math.cos(a), -math.sin(a), 0.0))
    org = Vector((r0*math.cos(a), r0*math.sin(a), z))
    ok, loc, nor, idx = btn.ray_cast(org, d, distance=dist, depsgraph=dg)
    if not ok:
        return None
    return (org - loc).length  # distance from axis-ish start radius

print("--- button outer radius vs z (angle 0/45/90, start r=6) ---")
for zi in range(0, 91, 2):
    z = zi * 0.1
    vals = []
    for ang in (0, 45, 90, 22.5):
        d = bcast(6, 6, 6.0, z, ang)
        vals.append('---' if d is None else f"{d:.3f}")
    print(f"  z={z:5.2f}  r={vals}")

print("--- button angular scan at z=8.8,8.6,8.4,8.2,8.0,7.6,7.0 (start r=4) ---")
for zi in (8.8, 8.65, 8.5, 8.3, 8.15, 8.0, 7.6, 7.0, 5.0, 1.0):
    vals = []
    for ang in range(0, 360, 10):
        d = bcast(4, 4, 4.0, zi, ang)
        vals.append('--' if d is None else f"{d:.2f}")
    print(f"  z={zi:5.2f}  " + ' '.join(vals))

print("--- button vertical scans (down from z=10) at r=0,0.5,1.0,1.5,2.0,2.2 ---")
for r in (0.0, 0.5, 1.0, 1.5, 2.0, 2.2):
    for ang in (0, 45):
        a = math.radians(ang)
        org = Vector((r*math.cos(a), r*math.sin(a), 12.0))
        ok, loc, nor, idx = btn.ray_cast(org, Vector((0,0,-1)), distance=20.0, depsgraph=dg)
        print(f"  r={r:.1f} ang={ang:3d} -> " + ('MISS' if not ok else f"z={loc.z:.4f} n={tuple(round(x,2) for x in nor)}"))
    print()

print("=== LID ===")
lid = bpy.data.objects['Enclosure_Lid']
lmw = lid.matrix_world
print("LID mw=", [round(v,4) for r in lmw for v in r])
print("LID dims", tuple(round(v,3) for v in lid.dimensions), "verts", len(lid.data.vertices))
CENTERS = [(-24.83, -35.47), (-24.83, -42.45), (-24.83, -49.47)]
for (cx, cy) in CENTERS:
    print(f"--- lid hole map at x={cx} y={cy} ---")
    print("   z    r_hit(ang0/45/90/135) from r=8 inward")
    for zi in range(630, 675, 2):
        z = zi * 0.1
        row = []
        for ang in (0, 45, 90, 135):
            a = math.radians(ang)
            org = Vector((cx + 8*math.cos(a), cy + 8*math.sin(a), z))
            d = Vector((-math.cos(a), -math.sin(a), 0.0))
            ok, loc, nor, idx = lid.ray_cast(org, d, distance=16.0, depsgraph=dg)
            row.append('--' if not ok else f"{(org-loc).length:5.2f}")
        print(f"  {z:6.2f}  " + ' '.join(row))
    print("   vertical: top surface z at r, and underside z at r")
    for r in (0.0, 0.5, 1.0, 1.5, 1.8, 2.0, 2.1, 2.2, 2.4, 2.6, 2.8, 3.0):
        org = Vector((cx + r, cy, 75.0))
        ok1, loc1, n1, i1 = lid.ray_cast(org, Vector((0,0,-1)), distance=30.0, depsgraph=dg)
        org2 = Vector((cx + r, cy, 50.0))
        ok2, loc2, n2, i2 = lid.ray_cast(org2, Vector((0,0,1)), distance=30.0, depsgraph=dg)
        print(f"    r={r:4.1f} top={loc1.z if ok1 else float('nan'):7.3f} "
              f"nz={n1.z if ok1 else 0:5.2f}  bottom={loc2.z if ok2 else float('nan'):7.3f} "
              f"nz2={n2.z if ok2 else 0:5.2f}")
    break

print("=== PCB switch tops at button centers ===")
for (cx, cy) in CENTERS:
    org = Vector((cx, cy, 70.0))
    hits = []
    for z in range(560, 590):
        ok, loc, nor, idx = sc.ray_cast(bpy.context.view_layer.depsgraph, org, Vector((0,0,-1)), distance=20.0)
        if ok:
            hits.append((loc.z, idx))
            break
    # find first object hit below
    org = Vector((cx, cy, 62.0))
    dgv = bpy.context.view_layer.depsgraph
    ok, loc, nor, idx, ob, mtx = sc.ray_cast(dgv, org, Vector((0,0,-1)), distance=15.0)
    if ok:
        print(f"  x={cx} y={cy} first hit below: {ob.name if ob else '?'} z={loc.z:.3f}")
    else:
        print(f"  x={cx} y={cy} first hit below: none")
print("DONE")
