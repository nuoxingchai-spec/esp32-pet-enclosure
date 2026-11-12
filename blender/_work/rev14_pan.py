import bpy, math
from mathutils import Vector
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)

def world_ray(obj, origin, direction):
    o = bpy.data.objects[obj]; mw = o.matrix_world; inv = mw.inverted()
    hit, loc, nor, idx = o.ray_cast(inv @ Vector(origin), (inv.to_3x3() @ Vector(direction)).normalized(), distance=500)
    if not hit: return None
    return mw @ loc, (mw.to_3x3().inverted().transposed() @ nor).normalized()

print("### Belly pan hole (20,30): ray +Z at radii")
for d in [0,0.4,0.7,1.0,1.1,1.2,1.3,1.5,1.8,2.0,2.1,2.2,2.4,2.6]:
    r = world_ray('Belly_Pan', (20+d, 30, 10), (0,0,1))
    print(f"  d={d:.2f} -> {None if not r else (round(r[0].z,3), tuple(round(v,2) for v in r[1]))}")
print("### Belly pan full top/bottom at no hole (0,0):")
for origin in ((0,0,10),(0,0,25)):
    d = (0,0,1) if origin[2] < 20 else (0,0,-1)
    r = world_ray('Belly_Pan', origin, d)
    print(origin, None if not r else (round(r[0].z,3), tuple(round(v,2) for v in r[1])))

print("### Belly pan vertex z histogram")
o = bpy.data.objects['Belly_Pan']
from collections import Counter
c = Counter(round((o.matrix_world@v.co).z,2) for v in o.data.vertices)
print(sorted(c.items()))

print("### Boss solid check: ray -Z from inside at (20,30) height 40")
r = world_ray('Enclosure_Body', (20,30,40), (0,0,-1))
print(None if not r else (round(r[0].z,3), tuple(round(v,2) for v in r[1])))
print("### Boss side faces at z=24: ring")
pts=[]
for v in bpy.data.objects['Enclosure_Body'].data.vertices:
    p = bpy.data.objects['Enclosure_Body'].matrix_world @ v.co
    if abs(p.z-24.0)<0.02 and math.hypot(p.x-20,p.y-30)<4:
        pts.append((round(p.x,3),round(p.y,3)))
print(sorted(set(pts))[:40])
