import bpy, os
from mathutils import Vector
ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
OUT = os.path.join(ROOT, r"blender\_work")

def setup(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    sc = bpy.context.scene
    body = bpy.data.objects['Enclosure_Body']
    for p in body.data.polygons:
        p.use_smooth = True
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
    return sc, body, cam

def render(sc, cam, tag, pos, tgt, lens):
    cam.location = pos; cam.data.lens = lens
    d = Vector(tgt) - Vector(pos)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(OUT, f'r7_{tag}.png')
    bpy.ops.render.render(write_still=True)

sc, body, cam = setup(os.path.join(ROOT, r"blender\robot_dog_enclosure_v3.blend"))
render(sc, cam, 'clean_smooth_seam', (120, -60, 57.4), (39.0, -50.0, 54.35), 150)
render(sc, cam, 'clean_smooth_mid', (100, -30, 58), (39, -25, 54.2), 130)
render(sc, cam, 'clean_smooth_q', (150, -120, 80), (36, -58, 47), 80)

sc, body, cam = setup(os.path.join(ROOT, r"blender\_work\rev6_corner.blend"))
render(sc, cam, 'corner_smooth_sh', (120, -95, 66), (36.5, -59.0, 52.0), 135)
render(sc, cam, 'corner_smooth_seam', (120, -60, 57.4), (39.0, -50.0, 54.35), 150)
render(sc, cam, 'corner_smooth_mid', (100, -30, 58), (39, -25, 54.2), 130)
render(sc, cam, 'corner_smooth_q', (150, -120, 80), (36, -58, 47), 80)
render(sc, cam, 'corner_smooth_front', (0, -135, 55.2), (0, -64, 54.35), 150)
print('DONE')
