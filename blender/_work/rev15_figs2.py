import bpy, bmesh, os, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT = r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5'
OUT = os.path.join(ROOT, r'blender\_review')
BLEND = os.path.join(ROOT, r'blender\robot_dog_enclosure_v3.blend')
bpy.ops.wm.open_mainfile(filepath=BLEND)
sc = bpy.context.scene
sh = sc.display.shading
sc.render.engine = 'BLENDER_WORKBENCH'
sh.light = 'STUDIO'; sh.studio_light = 'Default'; sh.color_type = 'OBJECT'
sh.show_cavity = True; sh.cavity_type = 'BOTH'
sh.curvature_ridge_factor = 1.0; sh.curvature_valley_factor = 1.0
sh.show_shadows = True; sh.shadow_intensity = 0.5; sh.show_object_outline = False
sc.render.film_transparent = False; sc.render.image_settings.file_format = 'PNG'
sc.view_settings.view_transform = 'Standard'; sc.world.color = (0.045, 0.045, 0.055)
COL = {
 'Enclosure_Body': (0.84, 0.84, 0.82, 1), 'Enclosure_Lid': (0.76, 0.76, 0.74, 1),
 'Face_Plate': (0.075, 0.075, 0.085, 1), 'Belly_Pan': (0.40, 0.40, 0.42, 1),
 'Leg_L': (0.96, 0.91, 0.83, 1), 'Leg_R': (0.96, 0.91, 0.83, 1),
 'Leg_L_Rear': (0.88, 0.83, 0.75, 1), 'Leg_R_Rear': (0.88, 0.83, 0.75, 1),
 'LED_Diffuser_Ring': (0.55, 0.80, 0.97, 1), 'Tail': (0.80, 0.62, 0.43, 1),
}
for n, c in COL.items():
    o = bpy.data.objects.get(n)
    if o: o.color = c
HIDE = {'Pet_Body_Blockout', 'V1_Base', 'V1_Lid', 'Cube', 'Preview_Ground'}
for n in HIDE:
    o = bpy.data.objects.get(n)
    if o: o.hide_render = True
for o in bpy.data.objects:
    if o.type in ('LIGHT', 'CAMERA'): o.hide_render = True
    if o.name.endswith('_Master'): o.hide_render = True
gm = bpy.data.meshes.new('GroundF'); g = bmesh.new()
bmesh.ops.create_grid(g, x_segments=1, y_segments=1, size=800)
g.to_mesh(gm); g.free()
ground = bpy.data.objects.new('GroundF', gm)
sc.collection.objects.link(ground); ground.location.z = -0.06
ground.color = (0.13, 0.13, 0.15, 1); ground.hide_render = True
cam_d = bpy.data.cameras.new('CF'); cam = bpy.data.objects.new('CF', cam_d)
sc.collection.objects.link(cam); sc.camera = cam
cam_d.clip_start = 0.2; cam_d.clip_end = 8000

def shot(name, loc, target, lens=55, res=(1800, 1500)):
    sc.render.resolution_x, sc.render.resolution_y = res
    cam.location = loc
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam_d.type = 'PERSP'; cam_d.lens = lens
    bpy.context.view_layer.update()
    sc.render.filepath = os.path.join(OUT, name + '.png')
    bpy.ops.render.render(write_still=True)
    print('SHOT', name, flush=True)

def px(p):
    co = world_to_camera_view(sc, cam, Vector(p))
    return [round(co.x * sc.render.resolution_x, 1), round((1 - co.y) * sc.render.resolution_y, 1)]

def save(name, anchors):
    d = {'image': name + '.png', 'res': [sc.render.resolution_x, sc.render.resolution_y],
         'anchors': {k: px(v) for k, v in anchors.items()}}
    open(os.path.join(OUT, 'anchors_' + name + '.json'), 'w', encoding='utf-8').write(json.dumps(d, indent=1))
    print('ANCH', name, d['anchors'], flush=True)

# exploded shell, clean: printed shell parts only
KEEP = ['Enclosure_Body', 'Enclosure_Lid', 'LED_Diffuser_Ring', 'Face_Plate', 'Belly_Pan',
        'Leg_L', 'Leg_R', 'Leg_L_Rear', 'Leg_R_Rear']
for o in bpy.data.objects:
    if o.type == 'MESH':
        o.hide_render = o.name not in KEEP
MOV = {'Enclosure_Lid': (0, 0, 42), 'LED_Diffuser_Ring': (0, 0, 46), 'Face_Plate': (0, 50, 0),
       'Belly_Pan': (0, 100, -17.2),
       'Leg_R': (30, 30, 0), 'Leg_L': (-30, 30, 0), 'Leg_R_Rear': (30, -30, 0), 'Leg_L_Rear': (-30, -30, 0)}
for n, (dx, dy, dz) in MOV.items():
    o = bpy.data.objects[n]; o.location = o.location + Vector((dx, dy, dz))
bpy.context.view_layer.update()
shot('71_exploded_shell', (300, 330, 210), (0, 45, 55), lens=50, res=(2500, 2000))
save('71_exploded_shell', {'body': (39, -8, 44), 'lid': (0, -18, 108.9), 'ring': (0, 63, 113.5),
                           'face': (0, 114.1, 31), 'pan': (0, 90, 1.3),
                           'leg_fr': (75, 74, 18), 'leg_fl': (-75, 74, 18),
                           'leg_rr': (75, -74, 18), 'leg_rl': (-75, -74, 18)})
# tail print orientation
for o in bpy.data.objects:
    if o.type == 'MESH': o.hide_render = True
tm = bpy.data.objects['Tail_Master']; tm.hide_render = False
tm.location = (0, 0, 0)
ground.hide_render = False
shot('83_tail_print', (55, -70, 48), (0, 0, 13), lens=70, res=(1600, 1500))
save('83_tail_print', {'tail': (0, -4, 12), 'base': (0, -42, 0.2)})
print('DONE2', flush=True)
