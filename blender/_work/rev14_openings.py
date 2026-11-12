import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
body = bpy.data.objects['Enclosure_Body']
bm = bmesh.new(); bm.from_mesh(body.data); bm.transform(body.matrix_world)
t = BVHTree.FromBMesh(bm)

def inside(x,y,z):
    o = Vector((-200,y,z)); dv = Vector((1,0,0)); n=0; last=-1e9
    while True:
        loc, nor, idx, dist = t.ray_cast(o, dv, 1000.0)
        if loc is None: break
        if loc.x - last > 0.2: n += 1; last = loc.x
        o = loc + dv*0.1
        if o.x > 200: break
    return n % 2 == 1

for z in (20.5, 22, 25, 28, 30, 32, 38, 40, 44, 48, 50, 52, 53.5, 54.5, 56, 57.5, 59.0, 59.9):
    print(f"Z={z:5.1f}")
    for y in (-60,-55,-50,-40,-30,-20,-10,0,10,20,30,40,50,55,60):
        free=[]; run=None
        for x in range(-39,40,1):
            m = inside(x,y,z)
            if (not m) and run is None: run=x
            if m and run is not None: free.append((run,x-1)); run=None
        if run is not None: free.append((run,39))
        spans = [f"{a}..{b}" for a,b in free if b-a>=1]
        print(f"   y={y:6.1f} free={spans}")
bm.free()
print("FRONT WALL first-hit y (from +Y):")
for z in (22,25,30,35,40,45,50,55,58):
    line=[]
    for x in range(-22,23,4):
        loc, nor, idx, dist = t.ray_cast(Vector((x,200,z)), Vector((0,-1,0)), 400.0)
        line.append(f"{loc.y:6.1f}" if loc else "  none")
    print(f" z={z:5.1f} " + " ".join(line))
print("BOTTOM first-hit z (from below):")
for y in (-55,-30,0,30,55):
    line=[]
    for x in (-36,-24,-12,0,12,24,36):
        loc, nor, idx, dist = t.ray_cast(Vector((x,y,-50)), Vector((0,0,1)), 300.0)
        line.append(f"{loc.z:5.1f}" if loc else " none")
    print(f" y={y:6.1f} " + " ".join(line))
