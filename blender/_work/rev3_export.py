import bpy, os

SRC = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage5b.blend"
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
OUTDIR = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\stl\v3"
bpy.ops.wm.open_mainfile(filepath=SRC)
os.makedirs(OUTDIR, exist_ok=True)

col = bpy.data.collections.get('RobotDog_v2')
if col: col.name = 'RobotDog_v3'

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

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('SAVED BLEND', BLEND)

for objname, outname in EXPORTS:
    o = bpy.data.objects.get(objname)
    if not o:
        print('MISSING', objname); continue
    was_vp = o.hide_viewport; was_set = o.hide_get(); was_render = o.hide_render
    o.hide_viewport = False; o.hide_render = False
    try: o.hide_set(False)
    except Exception: pass
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    path = os.path.join(OUTDIR, outname + '.stl')
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True,
                          global_scale=1.0, use_scene_unit=False,
                          apply_modifiers=True, ascii_format=False)
    print('EXPORT', outname, os.path.getsize(path))
    o.hide_viewport = was_vp; o.hide_render = was_render
    try: o.hide_set(was_set)
    except Exception: pass

print('DONE')
