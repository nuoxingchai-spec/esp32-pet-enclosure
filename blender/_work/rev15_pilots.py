import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend')
dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['Enclosure_Body']; ev=o.evaluated_get(dg); mw=o.matrix_world; inv=mw.inverted()
def cast(org, d, dist=100):
    ok,loc,nor,idx=ev.ray_cast(inv@Vector(org),(inv.to_3x3()@Vector(d)).normalized(),distance=dist)
    return (mw@loc) if ok else None
print('faceplate pilots (from y=75 toward -Y):')
for x in (-20.8,20.8):
    for z in (25.5,54.5):
        p=cast((x,75,z),(0,-1,0))
        print(f'  x{x} z{z}: {None if p is None else (round(p.x,2),round(p.y,3),round(p.z,2))} depth_from_61.8={None if p is None else round(61.8-p.y,3)}')
print('pan pilots (from z=10 toward +Z):')
for x in (-20,20):
    for y in (48,30,-50):
        p=cast((x,y,10),(0,0,1))
        print(f'  x{x} y{y}: {None if p is None else (round(p.x,2),round(p.y,2),round(p.z,3))} depth_from_20={None if p is None else round(p.z-20.0,3)}')
# leg pilot/shaft depth along X at the pivot; from outside +X at y=44,z=38
print('leg/servo shaft along -X from x=60:')
for y in (44,-44):
    p=cast((60,y,38),(-1,0,0))
    print(f'  y{y}: {None if p is None else (round(p.x,3),round(p.y,2),round(p.z,2))}')
