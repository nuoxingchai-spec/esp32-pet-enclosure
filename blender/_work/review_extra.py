import bpy, bmesh, math, os
from mathutils import Vector, Matrix

OUT = r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_review'
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.studio_light = 'Default'
scene.display.shading.show_shadows = True
scene.display.shading.shadow_intensity = 0.5
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = 'BOTH'
scene.display.shading.curvature_ridge_factor = 1.0
scene.display.shading.curvature_valley_factor = 1.0
scene.display.shading.color_type = 'OBJECT'
scene.display.shading.show_object_outline = False
scene.render.film_transparent = False
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'Standard'
try:
    scene.world.color = (0.045, 0.045, 0.055)
except Exception:
    w = bpy.data.worlds.new('W')
    scene.world = w
    w.color = (0.045, 0.045, 0.055)

COL = {
    'Enclosure_Body': (0.84, 0.84, 0.82, 1), 'Enclosure_Lid': (0.78, 0.78, 0.76, 1),
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
    'Button_Plunger_1': (0.93, 0.93, 0.92, 1), 'Button_Plunger_2': (0.93, 0.93, 0.92, 1),
    'Button_Plunger_3': (0.93, 0.93, 0.92, 1)}
for n, c in COL.items():
    o = bpy.data.objects.get(n)
    if o:
        o.color = c

HIDE_ALWAYS = {'Pet_Body_Blockout', 'V1_Base', 'V1_Lid', 'Cube', 'Preview_Ground'}
for n in HIDE_ALWAYS:
    o = bpy.data.objects.get(n)
    if o:
        o.hide_render = True
for lt in [o for o in bpy.data.objects if o.type in ('LIGHT', 'CAMERA')]:
    lt.hide_render = True

gm = bpy.data.meshes.new('GroundR')
g = bmesh.new()
bmesh.ops.create_grid(g, x_segments=1, y_segments=1, size=500)
g.to_mesh(gm)
g.free()
ground = bpy.data.objects.new('GroundR', gm)
scene.collection.objects.link(ground)
ground.location.z = -0.06
ground.color = (0.13, 0.13, 0.15, 1)

cam_data = bpy.data.cameras.new('CR')
cam = bpy.data.objects.new('CR', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.clip_start = 0.3
cam_data.clip_end = 5000


def look(t):
    cam.rotation_euler = (Vector(t) - cam.location).to_track_quat('-Z', 'Y').to_euler()


def all_meshes():
    return [o for o in bpy.data.objects if o.type == 'MESH'
            and o.name not in HIDE_ALWAYS and o.name != 'GroundR']


def show_all(except_names=()):
    for o in all_meshes():
        try:
            o.hide_render = o.name in except_names
        except ReferenceError:
            pass


def shot(name, loc, target, mode='PERSP', lens=55, ortho=120, res=(1500, 1500)):
    scene.render.resolution_x, scene.render.resolution_y = res
    cam.location = loc
    look(target)
    if mode == 'ORTHO':
        cam_data.type = 'ORTHO'
        cam_data.ortho_scale = ortho
    else:
        cam_data.type = 'PERSP'
        cam_data.lens = lens
    scene.render.filepath = os.path.join(OUT, name + '.png')
    bpy.ops.render.render(write_still=True)
    print('SHOT', name, flush=True)


show_all()
# full right side, landscape so the 128 mm body is not cropped
shot('03_right', (420, 0, 36), (0, 0, 36), mode='ORTHO', ortho=138, res=(1700, 1300))
# left side with the three button holes
shot('26_left_side', (-420, 0, 36), (0, 0, 36), mode='ORTHO', ortho=138, res=(1700, 1300))
# rear wall: USB-C and power switch
shot('27_rear_ports', (35, -195, 82), (0, -58, 55), lens=62, res=(1500, 1200))
# face plate screw + window corner detail
shot('28_face_screw_detail', (60, 250, 150), (-14, 62, 50), lens=135, res=(1500, 1300))

# microSD mock card, half inserted into the +X slot
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1)
bmesh.ops.scale(bm, vec=(15.0, 11.0, 1.0), verts=bm.verts)
bmesh.ops.translate(bm, vec=(41.5, -32.5, 57.25), verts=bm.verts)
me = bpy.data.meshes.new('SD_Card_Mock')
bm.to_mesh(me)
bm.free()
card = bpy.data.objects.new('SD_Card_Mock', me)
scene.collection.objects.link(card)
card.color = (0.95, 0.62, 0.18, 1)
show_all()
shot('14_sd_leg_clearance', (205, -155, 100), (39, -30, 50), lens=78, res=(1700, 1300))
bpy.data.objects.remove(card, do_unlink=True)
show_all()
shot('29_sd_slot_close', (175, -125, 85), (39, -31, 53), lens=90, res=(1600, 1300))
show_all()

print('EXTRA DONE', flush=True)
