import bpy, math
from mathutils import Vector
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)

def world_ray(obj, origin, direction):
    o = bpy.data.objects[obj]; mw = o.matrix_world; inv = mw.inverted()
    hit, loc, nor, idx = o.ray_cast(inv @ Vector(origin), (inv.to_3x3() @ Vector(direction)).normalized(), distance=500)
    if not hit: return None
    return mw @ loc, (mw.to_3x3().inverted().transposed() @ nor).normalized()

print("### front screw columns: interior wall from y=30 toward +Y")
for (x,z) in ((20.8,25.5),(-20.8,25.5),(20.8,54.5),(-20.8,54.5)):
    r = world_ray('Enclosure_Body', (x,30,z), (0,1,0))
    print(f"  ({x},{z}) inner={None if not r else (round(r[0].y,3), tuple(round(v,2) for v in r[1]))}")
print("### front boss radial extent at y=61.8 (ray -Y from front, x offsets)")
for dx in (0.0,0.8,1.0,1.2,1.5,2.0,2.5,3.0,3.5):
    r = world_ray('Enclosure_Body', (20.8+dx, 80, 25.5), (0,-1,0))
    print(f"  dx={dx:.1f} -> {None if not r else (round(r[0].y,3), tuple(round(v,2) for v in r[1]))}")
print("### face plate: screw seat ray -Y precise radii")
for dx in (0.0,0.5,1.0,1.1,1.14,1.2,1.5,1.8,2.0,2.15,2.25):
    r = world_ray('Face_Plate', (20.8+dx, 80, 25.5), (0,-1,0))
    print(f"  dx={dx:.2f} -> {None if not r else (round(r[0].y,4), tuple(round(v,2) for v in r[1]))}")
print("### bottom boss top / pilot bottom from above inside")
for (x,y) in ((20,30),(-20,30),(20,-50),(-20,-50),(20,48),(-20,48)):
    r = world_ray('Enclosure_Body', (x,y,45), (0,0,-1))
    print(f"  ({x},{y}) -> {None if not r else (round(r[0].z,3), tuple(round(v,2) for v in r[1]))}")
