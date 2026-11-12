import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)

def bvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t

pan=bvh(bpy.data.objects['Belly_Pan'])
face=bvh(bpy.data.objects['Face_Plate'])
def holes(t, origin, d, span, fixed, axis, label):
    print(label)
    for a in range(span[0], span[1]+1, 1):
        if axis=='z': o=Vector((a, fixed[0], origin)); dv=Vector((0,0,1))
        else: o=Vector((a, origin, fixed[0])); dv=Vector((0,1,0))
        loc,nor,idx,dist=t.ray_cast(o,dv,100.0)
        if loc is None:
            print(f"   {a}: MISS")
    # collect free spans
    free=[]; run=None
    for a in range(span[0], span[1]+1, 1):
        if axis=='z': o=Vector((a, fixed[0], origin)); dv=Vector((0,0,1))
        else: o=Vector((a, origin, fixed[0])); dv=Vector((0,1,0))
        loc,nor,idx,dist=t.ray_cast(o,dv,100.0)
        m = loc is not None
        if (not m) and run is None: run=a
        if m and run is not None: free.append((run,a-1)); run=None
    if run is not None: free.append((run,span[1]))
    print("   free x spans:", [f"{a}..{b}" for a,b in free if b-a>=1])
print("PAN ray from below at z=-50, holes=miss")
for y in (48.0,30.0,-50.0,-22.0,44.0,-44.0):
    holes(pan, -50.0, None, (-38,38), (y,), 'z', f"pan y={y}")
print("PAN row scan at x=20: free y spans (hole)")
free=[]; run=None
for y in range(-62,63,1):
    loc,nor,idx,dist=pan.ray_cast(Vector((20,y,-50)),Vector((0,0,1)),100.0)
    m=loc is not None
    if (not m) and run is None: run=y
    if m and run is not None: free.append((run,y-1)); run=None
if run is not None: free.append((run,62))
print("   x=20 free y:", [f"{a}..{b}" for a,b in free if b-a>=1])
free=[]; run=None
for y in range(-62,63,1):
    loc,nor,idx,dist=pan.ray_cast(Vector((-20,y,-50)),Vector((0,0,1)),100.0)
    m=loc is not None
    if (not m) and run is None: run=y
    if m and run is not None: free.append((run,y-1)); run=None
if run is not None: free.append((run,62))
print("   x=-20 free y:", [f"{a}..{b}" for a,b in free if b-a>=1])
print("FACEPLATE from front y=+200, holes=miss")
for z in (25.5,54.5,45.0,30.0,50.0):
    holes(face, 200.0, None, (-23,23), (z,), 'y', f"face z={z}")
