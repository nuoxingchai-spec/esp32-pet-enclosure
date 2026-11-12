import bpy
from mathutils import Vector
print("FILE", bpy.data.filepath)
names = ['Enclosure_Body','Enclosure_Lid','LED_Diffuser_Ring','Belly_Pan','Face_Plate','Button_Top_1','Ear_R','Tail','Leg_L','Touch_Module_Fit','PCB_Board','Battery_103450']
for n in names:
    o = bpy.data.objects.get(n)
    if not o:
        print('MISSING', n); continue
    b = [o.matrix_world @ Vector(c) for c in o.bound_box]
    zs = [p.z for p in b]
    mz = [v.co.z for v in o.data.vertices]
    t = o.matrix_world.translation
    print(f"X {n:18s} loc=({o.location.x:7.3f},{o.location.y:7.3f},{o.location.z:7.3f}) "
          f"mwt=({t.x:7.3f},{t.y:7.3f},{t.z:7.3f}) rotZ={o.rotation_euler.z:6.3f} scale=({o.scale.x:.3f},{o.scale.y:.3f},{o.scale.z:.3f}) "
          f"localz[{min(mz):7.2f},{max(mz):7.2f}] worldz[{min(zs):7.2f},{max(zs):7.2f}]")
