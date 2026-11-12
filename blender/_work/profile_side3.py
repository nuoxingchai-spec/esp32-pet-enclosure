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
    return (mw@loc).x
for y in (-60.0,-55.0,-50.0,-40.0,-30.0):
    print('y=',y)
    z=60.0
    while z>20:
        x=hx(y,z)
        print(f'  z{z:5.1f} '+('hole' if x is None else f'x{x:7.3f}'))
        z-=0.25
