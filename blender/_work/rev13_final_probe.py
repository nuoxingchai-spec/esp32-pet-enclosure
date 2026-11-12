import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import bmesh

BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
dg = bpy.context.evaluated_depsgraph_get()
lid = bpy.data.objects['Enclosure_Lid']
pc = bpy.data.objects['PCB_Components']

def bvh(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    t = BVHTree.FromBMesh(bm); bm.free(); return t

def cast(o, world_org, world_dir, dist=60):
    mw = o.matrix_world; mi = mw.inverted()
    org = mi @ Vector(world_org)
    d = (mi.to_3x3() @ Vector(world_dir)).normalized()
    ok, loc, nor, idx = o.ray_cast(org, d, distance=dist, depsgraph=dg)
    return (mw @ loc) if ok else None

for i in (1, 2, 3):
    b = bpy.data.objects[f'Button_Top_{i}']
    cx, cy = b.matrix_world.translation.x, b.matrix_world.translation.y
    hit = cast(b, (cx, cy, 80), (0, 0, -1))
    topz = hit.z if hit else float('nan')
    rad = 0.0
    for v in b.data.vertices:
        p = b.matrix_world @ v.co
        if p.z > 67.0 + 1e-6:
            rad = max(rad, math.hypot(p.x - cx, p.y - cy))
    hith = cast(lid, (cx, cy, 66.8), (1, 0, 0), 20)
    holer = (hith.x - cx) if hith else float('nan')
    hitt = cast(lid, (cx + 2.6, cy, 80), (0, 0, -1))
    top_ring = hitt.z if hitt else float('nan')
    hits = cast(pc, (cx, cy, 70), (0, 0, -1), 40)
    swz = hits.z if hits else float('nan')
    tl = bvh(lid)
    best = 1e9
    bm = bmesh.new(); bm.from_mesh(b.data); bm.transform(b.matrix_world)
    for v in bm.verts:
        loc, nor, idx, d = tl.find_nearest(v.co)
        if loc is not None and d < best: best = d
    bm.free()
    print(f"BTN{i} cap_top={topz:.3f} exposed_rad={rad:.3f} hole_rad={holer:.3f} "
          f"lid_top_ring={top_ring:.3f} switch_top={swz:.3f} min_gap_to_lid={best:.3f}")
print('DONE')
