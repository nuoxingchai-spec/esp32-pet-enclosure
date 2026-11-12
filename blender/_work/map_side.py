import bpy
from mathutils import Vector
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob=bpy.data.objects['Enclosure_Body']
dg=bpy.context.evaluated_depsgraph_get()
def hit(y,z):
    org=Vector((60,y,z)); d=Vector((-1,0,0))
    ok,loc,nor,idx=ob.ray_cast(org,d,distance=40.0, depsgraph=dg)
    if not ok: return ' '
    if loc.x>38.9: return '#'
    if loc.x>35.5: return '+'
    return '.'
# rear-right servo: y -65..-25, z 20..56
print('rear-right side map: # wall, + recess, . deep/hole, blank no hit')
print('    '+''.join(str(int(abs(y))//10%10) for y in range(-65,-24)))
for z in range(56,19,-1):
    row=''.join(hit(y+0.5,z-0.5) for y in range(-65,-25))
    print(f'{z:3d} '+row)
