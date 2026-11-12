import bpy
from mathutils import Vector
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
for name in ['Tail','Tail_Master','Enclosure_Body','Enclosure_Lid','LED_Diffuser_Ring','Face_Plate','Belly_Pan','Ear_R','Ear_L','Button_Top_1','Button_Top_2','Button_Top_3','Touch_Module_Fit']:
    o = bpy.data.objects.get(name)
    if not o:
        print('MISS', name); continue
    xs=[];ys=[];zs=[]
    for c in o.bound_box:
        p=o.matrix_world@Vector(c); xs.append(p.x);ys.append(p.y);zs.append(p.z)
    print(f"{name:20s} loc=({o.location.x:.2f},{o.location.y:.2f},{o.location.z:.2f}) "
          f"bbox x[{min(xs):.2f},{max(xs):.2f}] y[{min(ys):.2f},{max(ys):.2f}] z[{min(zs):.2f},{max(zs):.2f}] "
          f"v={len(o.data.vertices) if o.type=='MESH' else '-'}")
print('COLLECTIONS:')
for c in bpy.data.collections:
    print(' ', c.name, len(c.objects))
