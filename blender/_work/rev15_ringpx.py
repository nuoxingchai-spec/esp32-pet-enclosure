import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend')
sc=bpy.context.scene; cd=bpy.data.cameras.new('c'); cam=bpy.data.objects.new('c',cd); sc.collection.objects.link(cam); sc.camera=cam
sc.render.resolution_x,sc.render.resolution_y=2600,1900
cam.location=(255,285,175); cam.rotation_euler=(Vector((0,0,44))-cam.location).to_track_quat('-Z','Y').to_euler(); cd.lens=52
bpy.context.view_layer.update()
for p in [(20,62.5,69.5),(0,62.8,69.8),(30,63.2,69.8),(0,63.4,69.8),(-30,63.2,69.8),(36,40,69.8),(20,63.8,69.8)]:
    co=world_to_camera_view(sc,cam,Vector(p))
    print(p, round(co.x*2600,1), round((1-co.y)*1900,1))
