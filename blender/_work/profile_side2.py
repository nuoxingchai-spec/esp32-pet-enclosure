import bpy
from mathutils import Vector
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob=bpy.data.objects['Enclosure_Body']; mw=ob.matrix_world
dg=bpy.context.evaluated_depsgraph_get()
def hx(y,z):
    org=mw.inverted()@Vector((60,y,z)); d=(mw.to_3x3().inverted()@Vector((-1,0,0))).normalized()
    ok,loc,nor,idx=ob.ray_cast(org,d,distance=120.0,depsgraph=dg)
    if not ok: return None
    wx=(mw@loc).x
    return wx
ys=[-62.4,-62.0,-61.8,-61.6,-61.5,-61.4,-61.2,-61.0,-60.5,-60.0,-59.0,-58.0,-55.0,-50.0,-45.0,-35.0,-30.0,-27.0]
print('z  '+' '.join(f'{y:>6.1f}' for y in ys))
for z in [56,55,54.5,54,53,52,50,48,46,45,44,42,40,38,36,34,32,30,28,26,24,22,21]:
    vals=[]
    for y in ys:
        x=hx(y,z); vals.append('  hole' if x is None else f'{x:6.2f}')
    print(f'{z:2d} '+' '.join(vals))
