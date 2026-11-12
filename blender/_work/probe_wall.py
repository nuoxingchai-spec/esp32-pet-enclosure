import bpy, math
from mathutils import Vector
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
sc=bpy.context.scene
sc.render.engine='BLENDER_WORKBENCH'
sh=sc.display.shading
sh.light='STUDIO'; sh.studio_light='Default'; sh.color_type='OBJECT'
sh.show_cavity=True; sh.cavity_type='BOTH'
sh.curvature_ridge_factor=2.0; sh.curvature_valley_factor=2.0
sh.show_shadows=True; sh.shadow_intensity=0.4
sc.world.color=(0.8,0.82,0.86)
sc.render.resolution_x=1000; sc.render.resolution_y=1200
sc.render.image_settings.file_format='PNG'
bpy.data.objects['Preview_Ground'].hide_render=True
# hide legs + servos for clean wall view
for o in bpy.data.objects:
    if o.name.startswith('Leg_') or o.name.startswith('SG90_Fit'):
        o.hide_render=True
cam_d=bpy.data.cameras.new('C'); cam=bpy.data.objects.new('C',cam_d); sc.collection.objects.link(cam); sc.camera=cam
cam_d.type='ORTHO'; cam_d.ortho_scale=90
def look(pos,tgt):
    cam.location=pos; d=Vector(tgt)-Vector(pos); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
look((200,40,45),(39,40,45))
sc.render.filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\wall_ortho_right.png"
bpy.ops.render.render(write_still=True)
cam_d.type='PERSP'; cam_d.lens=85
look((115,75,68),(42,41,44))
sc.render.filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\wall_close_noleg.png"
bpy.ops.render.render(write_still=True)
print('done')
