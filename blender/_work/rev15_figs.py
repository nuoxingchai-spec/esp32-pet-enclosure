import bpy, bmesh, math, os, json
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
 'OLED_1p3_Module': (0.06, 0.06, 0.07, 1), 'OLED_ActiveArea': (0.28, 0.66, 0.95, 1),
 'LED_Diffuser_Ring': (0.55, 0.80, 0.97, 1),
 'SG90_Fit_1': (0.40, 0.58, 0.86, 1), 'SG90_Fit_2': (0.40, 0.58, 0.86, 1),
 'SG90_Fit_3': (0.40, 0.58, 0.86, 1), 'SG90_Fit_4': (0.40, 0.58, 0.86, 1),
 'Touch_Module_Fit': (0.92, 0.56, 0.22, 1),
 'PCB_Board': (0.10, 0.40, 0.22, 1), 'PCB_Components': (0.20, 0.56, 0.30, 1),
 'Battery_103450': (0.34, 0.35, 0.40, 1), 'Speaker_3070': (0.52, 0.52, 0.55, 1),
 'Button_Top_1': (0.97, 0.97, 0.94, 1), 'Button_Top_2': (0.97, 0.97, 0.94, 1), 'Button_Top_3': (0.97, 0.97, 0.94, 1),
 'Ear_R': (0.80, 0.62, 0.43, 1), 'Ear_L': (0.80, 0.62, 0.43, 1), 'Tail': (0.80, 0.62, 0.43, 1),
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

def shot(name, loc, target, mode='PERSP', lens=55, ortho=120, res=(1800, 1500)):
    sc.render.resolution_x, sc.render.resolution_y = res
    cam.location = loc
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    if mode == 'ORTHO':
        cam_d.type = 'ORTHO'; cam_d.ortho_scale = ortho
    else:
        cam_d.type = 'PERSP'; cam_d.lens = lens
    bpy.context.view_layer.update()
    sc.render.filepath = os.path.join(OUT, name + '.png')
    bpy.ops.render.render(write_still=True)
    print('SHOT', name, flush=True)

def px(p):
    co = world_to_camera_view(sc, cam, Vector(p))
    return [round(co.x * sc.render.resolution_x, 1), round((1 - co.y) * sc.render.resolution_y, 1)]

def save_anchors(name, anchors):
    d = {'image': name + '.png',
         'res': [sc.render.resolution_x, sc.render.resolution_y],
         'anchors': {k: px(v) for k, v in anchors.items()}}
    open(os.path.join(OUT, 'anchors_' + name + '.json'), 'w', encoding='utf-8').write(json.dumps(d, indent=1))
    print('ANCH', name, {k: px(v) for k, v in anchors.items()}, flush=True)

# ---------- 70 hero
ground.hide_render = False
shot('70_hero_label', (255, 285, 175), (0, 0, 44), lens=52, res=(2600, 1900))
A = {'body': (39.0, -8, 44), 'lid': (0, -18, 66.9), 'ring': (0, 62, 69.5),
     'face': (16, 64.1, 31), 'leg': (45, 45, 18), 'button': (-24.83, -42.45, 67.7),
     'ear': (21, 30, 74), 'tail': (0, -50, 84)}
save_anchors('70_hero_label', A)
ground.hide_render = True

# ---------- 71 exploded shell
MOV = {'Enclosure_Lid': (0, 0, 42), 'LED_Diffuser_Ring': (0, 0, 56), 'Face_Plate': (0, 50, 0),
       'Belly_Pan': (0, 100, -17.2),
       'Leg_R': (22, 18, 0), 'Leg_L': (-22, 18, 0), 'Leg_R_Rear': (22, -18, 0), 'Leg_L_Rear': (-22, -18, 0)}
orig = {}
for n, (dx, dy, dz) in MOV.items():
    o = bpy.data.objects[n]; orig[n] = o.location.copy()
    o.location = o.location + Vector((dx, dy, dz))
HIDE2 = ['Button_Top_1', 'Button_Top_2', 'Button_Top_3', 'Ear_R', 'Ear_L', 'Tail', 'Touch_Module_Fit']
for n in HIDE2:
    o = bpy.data.objects.get(n)
    if o: o.hide_render = True
bpy.context.view_layer.update()
shot('71_exploded_shell', (300, 330, 210), (0, 45, 55), lens=50, res=(2500, 2000))
A = {'body': (39, -8, 44), 'lid': (0, -18, 108.9), 'ring': (0, 63, 125.5),
     'face': (0, 114.1, 31), 'pan': (0, 90, 1.3),
     'leg_fr': (67, 62, 18), 'leg_fl': (-67, 62, 18), 'leg_rr': (67, -62, 18), 'leg_rl': (-67, -62, 18)}
save_anchors('71_exploded_shell', A)
for n, loc in orig.items():
    bpy.data.objects[n].location = loc
for n in HIDE2:
    o = bpy.data.objects.get(n)
    if o: o.hide_render = False
bpy.context.view_layer.update()

# ---------- 72 lid underside
for o in bpy.data.objects:
    if o.type == 'MESH': o.hide_render = True
for n in ['Enclosure_Lid', 'Button_Top_1', 'Button_Top_2', 'Button_Top_3', 'Ear_R', 'Ear_L',
          'Tail', 'Touch_Module_Fit', 'LED_Diffuser_Ring']:
    bpy.data.objects[n].hide_render = False
shot('72_lid_under_label', (95, 115, 6), (0, 0, 63.5), lens=58, res=(1900, 1600))
A = {'lid': (0, -20, 64.5), 'buttons': (-24.83, -42.45, 60.5), 'touch': (0, 35, 63.0),
     'ear_r': (21, 30, 64.0), 'ear_l': (-21, 30, 64.0), 'tail_socket': (0, -43, 64.0),
     'lip': (36.29, 0, 59.7), 'ring': (0, 63, 68.5)}
save_anchors('72_lid_under_label', A)

# ---------- 73 internal deck
for o in bpy.data.objects:
    if o.type == 'MESH': o.hide_render = True
for n in ['PCB_Board', 'PCB_Components', 'OLED_1p3_Module', 'OLED_ActiveArea',
          'SG90_Fit_1', 'SG90_Fit_2', 'SG90_Fit_3', 'SG90_Fit_4',
          'Battery_103450', 'Speaker_3070', 'Leg_L', 'Leg_R', 'Leg_L_Rear', 'Leg_R_Rear']:
    bpy.data.objects[n].hide_render = False
shot('73_int_label', (190, -210, 150), (0, -5, 42), lens=55, res=(1900, 1600))
A = {'pcb': (0, -8, 55.0), 'oled': (0, 61.2, 45), 'battery': (0, -34, 30.2),
     'speaker': (0, 8, 44), 'servo': (25, 44, 44.1), 'leg': (44, 44, 18)}
save_anchors('73_int_label', A)

# ---------- 80-82 screws
for o in bpy.data.objects:
    if o.type == 'MESH' and not o.name.endswith('_Master') and o.name not in HIDE and o.name != 'GroundF':
        o.hide_render = False
ground.hide_render = True
shot('80_screw_front', (0, 320, 40), (0, 0, 40), mode='ORTHO', ortho=150, res=(1800, 1500))
A = {}
for x in (-20.8, 20.8):
    for z in (25.5, 54.5):
        A['f_%s_%s' % (x, z)] = (x, 64.3, z)
save_anchors('80_screw_front', A)
shot('81_screw_bottom', (0, 0, -220), (0, 0, 40), mode='ORTHO', ortho=150, res=(1800, 1500))
A = {}
for x in (-20, 20):
    for y in (48, 30, -50):
        A['b_%s_%s' % (x, y)] = (x, y, 16.9)
save_anchors('81_screw_bottom', A)
shot('82_screw_side', (320, 0, 40), (0, 0, 40), mode='ORTHO', ortho=150, res=(1800, 1500))
A = {'s_%s' % y: (48.2, y, 38) for y in (44, -44)}
save_anchors('82_screw_side', A)

# ---------- 83 tail print orientation
for o in bpy.data.objects:
    if o.type == 'MESH': o.hide_render = True
tm = bpy.data.objects['Tail_Master']; tm.hide_render = False
tm.location = (0, 0, 0)
ground.hide_render = False
shot('83_tail_print', (90, -120, 75), (0, 0, 15), lens=60, res=(1700, 1500))
A = {'tail': (0, -5, 14)}
save_anchors('83_tail_print', A)
print('FIGS DONE', flush=True)
