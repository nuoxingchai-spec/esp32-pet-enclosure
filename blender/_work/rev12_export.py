import bpy, os
from mathutils import Vector

BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
OUTDIR = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\stl\v3"
bpy.ops.wm.open_mainfile(filepath=BLEND)
os.makedirs(OUTDIR, exist_ok=True)

EXPORTS = [
    ('Enclosure_Body', 'Enclosure_Body'),
    ('Enclosure_Lid', 'Enclosure_Lid'),
    ('Face_Plate', 'Face_Plate'),
    ('Belly_Pan', 'Belly_Pan'),
    ('LED_Diffuser_Ring', 'LED_Diffuser_Ring'),
    ('Leg_L', 'Leg_L'),
    ('Leg_R', 'Leg_R'),
    ('Button_Top_Master', 'Button_Top'),
    ('Ear_R_Master', 'Ear_R'),
    ('Ear_L_Master', 'Ear_L'),
    ('Tail_Master', 'Tail'),
]

PRINT = ['Enclosure_Body','Enclosure_Lid','Face_Plate','Belly_Pan','LED_Diffuser_Ring',
         'Leg_R','Leg_R_Rear','Leg_L','Leg_L_Rear','Button_Top_1','Button_Top_2','Button_Top_3',
         'Ear_R','Ear_L','Tail']
xs=[]; ys=[]; zs=[]
for n in PRINT:
    o = bpy.data.objects[n]
    for c in o.bound_box:
        p = o.matrix_world @ Vector(c); xs.append(p.x); ys.append(p.y); zs.append(p.z)
print(f"PRINT-BBOX x[{min(xs):.2f},{max(xs):.2f}] y[{min(ys):.2f},{max(ys):.2f}] z[{min(zs):.2f},{max(zs):.2f}]"
      f"  size {max(xs)-min(xs):.2f} x {max(ys)-min(ys):.2f} x {max(zs)-min(zs):.2f}")

for objname, outname in EXPORTS:
    o = bpy.data.objects.get(objname)
    if not o:
        print('MISSING', objname); continue
    was_hv = o.hide_viewport; was_set = o.hide_get(); was_render = o.hide_render
    o.hide_viewport = False; o.hide_render = False
    try: o.hide_set(False)
    except Exception: pass
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    path = os.path.join(OUTDIR, outname + '.stl')
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True,
                          global_scale=1.0, use_scene_unit=False,
                          apply_modifiers=True, ascii_format=False)
    print('EXPORT', outname, os.path.getsize(path))
    o.hide_viewport = was_hv; o.hide_render = was_render
    try: o.hide_set(was_set)
    except Exception: pass
print('DONE')
