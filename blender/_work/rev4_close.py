import bpy, os
from mathutils import Vector
ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, r"blender\_work\rev4_stage.blend"))
sc = bpy.context.scene
body = bpy.data.objects['Enclosure_Body']
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading
sh.light = 'STUDIO'; sh.studio_light = 'Default'; sh.color_type = 'OBJECT'
sh.show_cavity = True; sh.cavity_type = 'BOTH'
sh.curvature_ridge_factor = 2.0; sh.curvature_valley_factor = 2.0
sh.show_shadows = True; sh.shadow_intensity = 0.35
sc.world.color = (0.82, 0.85, 0.9)
sc.render.resolution_x = 1200; sc.render.resolution_y = 900
sc.render.image_settings.file_format = 'PNG'
for o in sc.objects:
    if o.type == 'MESH' and o.name != 'Enclosure_Body':
        o.hide_render = True
cam_d = bpy.data.cameras.new('C'); cam = bpy.data.objects.new('C', cam_d)
sc.collection.objects.link(cam); sc.camera = cam
def look(pos, tgt, lens):
    cam.location = pos; cam.data.lens = lens
    d = Vector(tgt) - Vector(pos)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
VIEWS = [
    ('close_sh', (120, -95, 66), (36.5, -59.0, 52.0), 135),
    ('close_seam', (120, -60, 57.4), (39.0, -50.0, 54.35), 150),
    ('close_back', (120, -95, 62), (36.5, 59.0, 53.0), 135),
]
for tag, pos, tgt, lens in VIEWS:
    look(pos, tgt, lens)
    sc.render.filepath = os.path.join(ROOT, rf"blender\_work\r4_{tag}.png")
    bpy.ops.render.render(write_still=True)
print('DONE')
