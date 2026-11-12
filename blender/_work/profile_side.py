import bpy
from mathutils import Vector
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob=bpy.data.objects['Enclosure_Body']; mw=ob.matrix_world
dg=bpy.context.evaluated_depsgraph_get()
def hx(y,z):
    org=mw.inverted()@Vector((60,y,z)); d=(mw.to_3x3().inverted()@Vector((-1,0,0))).normalized()
    ok,loc,nor,idx=ob.ray_cast(org,d,distance=120.0,depsgraph=dg)
    return None if not ok else (mw@loc).x
for z in (52,50,46,42,34,28):
    print('z=',z)
    y=-64.0
    while y<-24:
        x=hx(y,z)
        if x is None: print(f'  y{y:6.1f} HOLE')
        elif x<38.7: print(f'  y{y:6.1f} x{x:6.2f}')
        y+=0.2
