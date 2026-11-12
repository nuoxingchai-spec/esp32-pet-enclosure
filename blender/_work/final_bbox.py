import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend")
tm=bpy.data.objects['Touch_Module_Fit']
bb=[tm.matrix_world @ Vector(c) for c in tm.bound_box]
print('TOUCH world', 'x', round(min(p.x for p in bb),2), round(max(p.x for p in bb),2), 'y', round(min(p.y for p in bb),2), round(max(p.y for p in bb),2), 'z', round(min(p.z for p in bb),2), round(max(p.z for p in bb),2))
xs=[];ys=[];zs=[]
names=['Enclosure_Body','Enclosure_Lid','Face_Plate','Belly_Pan','LED_Diffuser_Ring','Leg_R','Leg_R_Rear','Leg_L','Leg_L_Rear','Button_Top_1','Button_Top_2','Button_Top_3','Ear_R','Ear_L','Tail']
for n in names:
    o=bpy.data.objects[n]
    for c in o.bound_box:
        p=o.matrix_world @ Vector(c); xs.append(p.x); ys.append(p.y); zs.append(p.z)
print('ASM bbox', round(min(xs),2), round(max(xs),2), round(min(ys),2), round(max(ys),2), round(min(zs),2), round(max(zs),2), 'size', round(max(xs)-min(xs),2), round(max(ys)-min(ys),2), round(max(zs)-min(zs),2))
print('COL', [c.name for c in bpy.data.collections])
print('DONE')
