import bpy, bmesh, math
from mathutils import Vector

F = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob = bpy.data.objects['Enclosure_Body']
mw = ob.matrix_world
bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(mw)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()

def in_rr_corner(p):
    return p.x > 30.0 and p.y < -55.0
def in_rr_flat(p):
    return p.x > 38.0 and -55.0 <= p.y <= -45.0

print("=== faces with a vertex at z54.35, RR corner ===")
cnt = 0
for f in bm.faces:
    zs = [v.co.z for v in f.verts]
    if not (min(zs) < 54.40 and max(zs) > 54.30): continue
    c = f.calc_center_median()
    if not in_rr_corner(c): continue
    if abs(c.z - 54.35) > 0.2: continue
    cnt += 1
    vs = [tuple(round(q, 3) for q in v.co) for v in f.verts]
    print(f"f{cnt:3d} n=({f.normal.x:5.2f},{f.normal.y:5.2f},{f.normal.z:5.2f}) A={f.calc_area():7.4f} z=[{min(zs):.3f},{max(zs):.3f}] c=({c.x:.2f},{c.y:.2f}) verts={vs}")
print('corner faces at seam:', cnt)

print("\n=== faces with a vertex at z54.35, RR flat ===")
cnt = 0
for f in bm.faces:
    zs = [v.co.z for v in f.verts]
    if not (min(zs) < 54.40 and max(zs) > 54.30): continue
    c = f.calc_center_median()
    if not in_rr_flat(c): continue
    if abs(c.z - 54.35) > 0.2: continue
    cnt += 1
    vs = [tuple(round(q, 3) for q in v.co) for v in f.verts]
    print(f"f{cnt:3d} n=({f.normal.x:5.2f},{f.normal.y:5.2f},{f.normal.z:5.2f}) A={f.calc_area():7.4f} z=[{min(zs):.3f},{max(zs):.3f}] c=({c.x:.2f},{c.y:.2f}) verts={vs}")
print('flat faces at seam:', cnt)

print("\n=== all verts at z54.35 RR quadrant with adjacency ===")
for v in bm.verts:
    if abs(v.co.z - 54.35) > 0.02: continue
    if not (v.co.x > 30.0 and v.co.y < -55.0): continue
    above = [f for f in v.link_faces if max(q.co.z for q in f.verts) > 54.40]
    below = [f for f in v.link_faces if min(q.co.z for q in f.verts) < 54.30]
    flat = [f for f in v.link_faces if abs(f.normal.z) > 0.9]
    print(f"v({v.co.x:7.3f},{v.co.y:8.3f}) deg={len(v.link_faces)} above={len(above)} below={len(below)} horiz={len(flat)}")

print("\n=== vertical rays down from z=54.60: fin top map RR ===")
mi = mw.inverted(); M3 = mw.to_3x3(); M3i = M3.inverted(); dg = bpy.context.evaluated_depsgraph_get()
for gy in [ -55.5, -56.5, -57.5, -58.5, -59.5, -60.5, -61.5, -62.0, -62.5 ]:
    row=[]
    for gx in [33,34,35,36,37,38,38.5,39]:
        ok,loc,nor,idx = ob.ray_cast(mi @ Vector((gx, gy, 54.60)), (M3i @ Vector((0,0,-1))).normalized(), distance=5.0, depsgraph=dg)
        row.append("  air " if not ok else f"{ (mw@loc).z:6.2f}")
    print(f"y{gy:6.1f} " + " ".join(row))
print('   x:     33     34     35     36     37     38    38.5    39')
bm.free()
print('DONE')
