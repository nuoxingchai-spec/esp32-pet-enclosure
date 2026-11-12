import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage3.blend')
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for z in (58.9,59.2,59.5,59.8,60.2,60.6,61.0,61.4,61.7):
    hit,loc,nor,idx,obj,mat=sc.ray_cast(dg,Vector((0,100,z)),Vector((0,-1,0)))
    print(f'z={z}: {obj.name if obj else None} at y={loc.y:.2f}' if hit else f'z={z}: none')
# hide face plate, repeat
fp=bpy.data.objects.get('Face_Plate')
if fp: fp.hide_viewport=True
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
print('--- no face plate ---')
for z in (58.9,59.2,59.5,59.8,60.2,60.6,61.0,61.4,61.7):
    hit,loc,nor,idx,obj,mat=sc.ray_cast(dg,Vector((0,100,z)),Vector((0,-1,0)))
    print(f'z={z}: {obj.name if obj else None} at y={loc.y:.2f}' if hit else f'z={z}: none')
