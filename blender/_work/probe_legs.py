import bpy, math
from mathutils import Vector
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
sc=bpy.context.scene
sc.render.engine='BLENDER_WORKBENCH'
sc.display.shading.light='STUDIO'
sc.display.shading.studio_light='Default'
sc.display.shading.color_type='OBJECT'
sc.display.shading.show_cavity=True
sc.display.shading.cavity_type='BOTH'
sc.display.shading.curvature_ridge_factor=1.5
sc.display.shading.curvature_valley_factor=1.2
sc.display.shading.show_shadows=True
sc.display.shading.shadow_intensity=0.35
sc.render.film_transparent=False
sc.world.color=(0.85,0.87,0.90)
sc.render.resolution_x=1000; sc.render.resolution_y=1200
sc.render.image_settings.file_format='PNG'
# hide fit/ground/checkers for clarity
for n in ['Preview_Ground']:
    o=bpy.data.objects.get(n)
    if o: o.hide_render=True
cam_d=bpy.data.cameras.new('PCam'); cam=bpy.data.objects.new('PCam',cam_d); sc.collection.objects.link(cam); sc.camera=cam
cam_d.lens=80
def look(pos,tgt):
    cam.location=pos
    d=Vector(tgt)-Vector(pos)
    cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
views=[('FR',(115,75,68),(42,41,44)),('RR',(115,-75,68),(42,-41,44)),
       ('FL',(-115,75,68),(-42,41,44)),('RL',(-115,-75,68),(-42,-41,44))]
for name,pos,tgt in views:
    look(pos,tgt)
    sc.render.filepath=rf"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\probe_leg_{name}.png"
    bpy.ops.render.render(write_still=True)
    print('WROTE',sc.render.filepath)
