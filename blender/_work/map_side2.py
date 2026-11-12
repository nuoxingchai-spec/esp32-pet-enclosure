import bpy
from mathutils import Vector
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob=bpy.data.objects['Enclosure_Body']; mw=ob.matrix_world
dg=bpy.context.evaluated_depsgraph_get()
def hit(y,z):
    org=mw.inverted()@Vector((60,y,z)); d=(mw.to_3x3().inverted()@Vector((-1,0,0))).normalized()
    ok,loc,nor,idx=ob.ray_cast(org,d,distance=120.0,depsgraph=dg)
    if not ok: return ' '
    wx=(mw@loc).x
    if wx>38.9: return '#'
    if wx>35.5: return '+'
    return '.'
print('rear-right side map (world y/z): # wall x>38.9, + recess 35.5-38.9, . deeper, blank no hit')
for z in range(56,19,-1):
    row=''.join(hit(y+0.5,z-0.5) for y in range(-65,-25))
    print(f'{z:3d} '+row)
