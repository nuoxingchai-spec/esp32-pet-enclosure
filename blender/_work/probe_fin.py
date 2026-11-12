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
sh.show_shadows=True; sh.shadow_intensity=0.35
sc.world.color=(0.82,0.85,0.9)
sc.render.resolution_x=900; sc.render.resolution_y=1100
sc.render.image_settings.file_format='PNG'
bpy.data.objects['Preview_Ground'].hide_render=True
for n in ['Enclosure_Lid','LED_Diffuser_Ring','Ear_L','Ear_R','Tail']:
    o=bpy.data.objects.get(n)
    if o: o.hide_render=True
cam_d=bpy.data.cameras.new('C'); cam=bpy.data.objects.new('C',cam_d); sc.collection.objects.link(cam); sc.camera=cam
cam_d.lens=100
def look(pos,tgt):
    cam.location=pos; d=Vector(tgt)-Vector(pos); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
look((105,-70,58),(39,-52,51))
sc.render.filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\fin_withleg.png"
bpy.ops.render.render(write_still=True)
for o in bpy.data.objects:
    if o.name.startswith('Leg_'): o.hide_render=True
sc.render.filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\fin_noleg.png"
bpy.ops.render.render(write_still=True)
print('done')
