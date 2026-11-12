import bpy, math
from mathutils import Vector

BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)

deps = bpy.context.evaluated_depsgraph_get()

def world_ray(obj, origin, direction):
    o = bpy.data.objects[obj]
    mw = o.matrix_world
    inv = mw.inverted()
    o_local = inv @ Vector(origin)
    d_local = (inv.to_3x3() @ Vector(direction)).normalized()
    hit, loc, nor, idx = o.ray_cast(o_local, d_local, distance=500)
    if not hit:
        return None
    wl = mw @ loc
    wn = (mw.to_3x3().inverted().transposed() @ nor).normalized()
    return wl, wn

print("### Face plate screw at (20.8, 25.5): ray -Y from y=80, x offsets")
for dx in (0, 0.6, 1.0, 1.15, 1.3, 1.6, 2.0, 2.1, 2.3):
    r = world_ray('Face_Plate', (20.8+dx, 80, 25.5), (0,-1,0))
    print(f"  dx={dx:.2f} -> {None if not r else (round(r[0].y,3), tuple(round(v,2) for v in r[1]))}")

print("### Body behind faceplate at same ray")
for dx in (0, 0.9, 1.0, 1.3, 2.3):
    r = world_ray('Enclosure_Body', (20.8+dx, 80, 25.5), (0,-1,0))
    print(f"  dx={dx:.2f} -> {None if not r else (round(r[0].y,3), tuple(round(v,2) for v in r[1]))}")

print("### Belly pan + body at (20,30): ray +Z from z=10")
for d in (0, 0.6, 1.0, 1.15, 1.5, 2.0):
    rp = world_ray('Belly_Pan', (20+d, 30, 10), (0,0,1))
    rb = world_ray('Enclosure_Body', (20+d, 30, 10), (0,0,1))
    print(f"  d={d:.2f} pan={None if not rp else (round(rp[0].z,3), tuple(round(v,2) for v in rp[1]))} "
          f"body={None if not rb else (round(rb[0].z,3), tuple(round(v,2) for v in rb[1]))}")

print("### Leg_R outer at (y=44,z=38): ray -X from x=60")
for dz in (0, 0.5, 0.9, 1.1, 1.3, 1.6, 2.0, 2.2):
    r = world_ray('Leg_R', (60, 44, 38+dz), (-1,0,0))
    print(f"  dz={dz:.2f} -> {None if not r else (round(r[0].x,3), tuple(round(v,2) for v in r[1]))}")

print("### leg top U-slot / hub region x ray at x=44,z=38 offsets")
for dy in (-1.5, -1.0, -0.6, 0, 0.6, 1.0, 1.5):
    r = world_ray('Leg_R', (60, 44+dy, 38), (-1,0,0))
    print(f"  dy={dy:.2f} -> {None if not r else (round(r[0].x,3), tuple(round(v,2) for v in r[1]))}")

print("### Body front face around face plate: ray -Y at x=20.8 z offsets")
for dz in (0, 1.0, 1.2, 1.5, 2.0):
    r = world_ray('Enclosure_Body', (20.8, 80, 25.5+dz), (0,-1,0))
    print(f"  dz={dz:.2f} -> {None if not r else (round(r[0].y,3), tuple(round(v,2) for v in r[1]))}")

print("### Face plate thickness at non-hole location x=10")
for y in (64.05, 63.9, 63.0, 62.0, 61.85):
    r = world_ray('Face_Plate', (10, 80, 30), (0,-1,0))
    print('   ', r)
