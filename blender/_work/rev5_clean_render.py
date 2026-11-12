import bpy, os, math
from mathutils import Vector
ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
OUT = os.path.join(ROOT, r"blender\_work")
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, r"blender\robot_dog_enclosure_v3.blend"))
sc = bpy.context.scene
for o in sc.objects:
    if o.type == 'MESH' and o.name != 'Enclosure_Body':
        o.hide_render = True; o.hide_viewport = True
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading
sh.light = 'STUDIO'; sh.studio_light = 'Default'; sh.color_type = 'OBJECT'
sh.show_cavity = True; sh.cavity_type = 'BOTH'
sh.curvature_ridge_factor = 2.0; sh.curvature_valley_factor = 2.0
sh.show_shadows = True; sh.shadow_intensity = 0.35
sc.world.color = (0.82, 0.85, 0.9)
sc.render.resolution_x = 1200; sc.render.resolution_y = 900
sc.render.image_settings.file_format = 'PNG'
cam_d = bpy.data.cameras.new('C'); cam = bpy.data.objects.new('C', cam_d)
sc.collection.objects.link(cam); sc.camera = cam
def look(pos, tgt, lens):
    cam.location = pos; cam.data.lens = lens
    d = Vector(tgt) - Vector(pos)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
VIEWS = [
    ('clean_mid', (100, -30, 58), (39, -25, 54.2), 130),
    ('clean_seam', (120, -60, 57.4), (39.0, -50.0, 54.35), 150),
    ('clean_mid_cav', (100, -30, 58), (39, -25, 54.2), 130),
]
for tag, pos, tgt, lens in VIEWS:
    if tag.endswith('cav'):
        sh.show_cavity = False; sh.show_shadows = False
    look(pos, tgt, lens)
    sc.render.filepath = os.path.join(OUT, f'r5_{tag}.png')
    bpy.ops.render.render(write_still=True)
print('DONE')
