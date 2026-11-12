import bpy, bmesh, math, os
from mathutils import Vector

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
for n in ['Pet_Body_Blockout', 'V1_Base', 'V1_Lid', 'Cube', 'Preview_Ground']:
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
cam_data.clip_start = 0.5
cam_data.clip_end = 5000


def look(t):
    cam.rotation_euler = (Vector(t) - cam.location).to_track_quat('-Z', 'Y').to_euler()


def all_meshes():
    return [o for o in bpy.data.objects if o.type == 'MESH' and o.name != 'GroundR']


def show_only(names):
    for o in all_meshes():
        try:
            o.hide_render = o.name not in names
        except ReferenceError:
            pass


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


INTERNALS = {'OLED_1p3_Module', 'OLED_ActiveArea', 'PCB_Board', 'PCB_Components',
             'Battery_103450', 'Speaker_3070', 'Touch_Module_Fit'}

leg = bpy.data.objects['Leg_R']
dup = leg.copy()
dup.data = leg.data.copy()
scene.collection.objects.link(dup)
dup.name = 'Leg_R_cut'
fit = bpy.data.objects['SG90_Fit_1']
dupf = fit.copy()
dupf.data = fit.data.copy()
scene.collection.objects.link(dupf)
dupf.name = 'Horn_cut'
cut = bpy.data.meshes.new('c')
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1)
bmesh.ops.scale(bm, vec=(200, 300, 300), verts=bm.verts)
bmesh.ops.translate(bm, vec=(141.5, 44, 40), verts=bm.verts)
bm.to_mesh(cut)
bm.free()
co = bpy.data.objects.new('c', cut)
scene.collection.objects.link(co)
for tgt in (dup, dupf):
    md = tgt.modifiers.new('b', 'BOOLEAN')
    md.operation = 'DIFFERENCE'
    md.solver = 'EXACT'
    md.object = co
    bpy.context.view_layer.objects.active = tgt
    tgt.select_set(True)
    bpy.ops.object.modifier_apply(modifier=md.name)
bpy.data.objects.remove(co, do_unlink=True)
bpy.data.objects.remove(leg, do_unlink=True)
bpy.data.objects.remove(fit, do_unlink=True)
dup.color = (0.96, 0.91, 0.83, 1)
dupf.color = (0.40, 0.58, 0.86, 1)
show_only({'Leg_R_cut', 'Horn_cut'})
cam_data.type = 'PERSP'
cam_data.lens = 90
cam_data.clip_start = 0.2
scene.render.resolution_x = 1400
scene.render.resolution_y = 1400
cam.location = (210, 80, 44)
look((41.5, 44, 32))
scene.render.filepath = os.path.join(OUT, '19_section_leg_horn.png')
bpy.ops.render.render(write_still=True)
print('SHOT 19', flush=True)
bpy.data.objects.remove(dup, do_unlink=True)
bpy.data.objects.remove(dupf, do_unlink=True)

show_all(except_names=('Enclosure_Lid', 'LED_Diffuser_Ring'))
shot('20_open_lid', (175, 195, 225), (0, 0, 48), lens=52, res=(1700, 1400))
show_only(INTERNALS | {'SG90_Fit_1', 'SG90_Fit_2', 'SG90_Fit_3', 'SG90_Fit_4'})
shot('21_internals', (205, 225, 190), (0, 0, 44), lens=55, res=(1700, 1300))
show_only({'Leg_R', 'Leg_L', 'Leg_R_Rear', 'Leg_L_Rear',
           'SG90_Fit_1', 'SG90_Fit_2', 'SG90_Fit_3', 'SG90_Fit_4'})
shot('22_drive_layout', (210, 190, 150), (0, 0, 30), lens=55, res=(1600, 1300))
show_all()
ground.hide_render = True
shot('23_top', (0, 0, 320), (0, 0, 66), mode='ORTHO', ortho=145, res=(1400, 1500))
ground.hide_render = False
shot('24_rear_low', (-175, -230, 85), (0, 0, 40), lens=50, res=(1700, 1300))
show_all(except_names=('OLED_ActiveArea',))
ground.hide_render = True
shot('25_bottom', (0, 0, -320), (0, 0, 30), mode='ORTHO', ortho=150, res=(1500, 1300))
print('ALL DONE', flush=True)
