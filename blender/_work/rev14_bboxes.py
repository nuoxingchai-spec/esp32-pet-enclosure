import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend")
for n in ('Battery_103450','Speaker_3070','SG90_Fit_1','SG90_Fit_2','SG90_Fit_3','SG90_Fit_4','Belly_Pan','OLED_1p3_Module','PCB_Board','PCB_Components','Touch_Module_Fit'):
    o=bpy.data.objects[n]; pts=[o.matrix_world@Vector(c) for c in o.bound_box]
    print(n, tuple(round(min(p[i] for p in pts),2) for i in range(3)), tuple(round(max(p[i] for p in pts),2) for i in range(3)))
