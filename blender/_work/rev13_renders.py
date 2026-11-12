import bpy, bmesh, math, os
from mathutils import Vector

ROOT = r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5'
OUT = os.path.join(ROOT, r'blender\_review')
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, r'blender\robot_dog_enclosure_v3.blend'))
sc = bpy.context.scene
sh = sc.display.shading
sc.render.engine = 'BLENDER_WORKBENCH'
sh.light = 'STUDIO'; sh.studio_light = 'Default'; sh.color_type = 'OBJECT'
sh.show_cavity = True; sh.cavity_type = 'BOTH'
sh.curvature_ridge_factor = 1.0; sh.curvature_valley_factor = 1.0
sh.show_shadows = True; sh.shadow_intensity = 0.5
sh.studiolight_rotate_z = 0.0
sh.show_object_outline = False
sc.render.film_transparent = False
sc.render.image_settings.file_format = 'PNG'
sc.view_settings.view_transform = 'Standard'
sc.world.color = (0.045, 0.045, 0.055)

COL = {
    'Enclosure_Body': (0.84,0.84,0.82,1), 'Enclosure_Lid': (0.76,0.76,0.74,1),
    'Face_Plate': (0.075,0.075,0.085,1), 'Belly_Pan': (0.40,0.40,0.42,1),
    'Leg_L': (0.96,0.91,0.83,1), 'Leg_R': (0.96,0.91,0.83,1),
    'Leg_L_Rear': (0.88,0.83,0.75,1), 'Leg_R_Rear': (0.88,0.83,0.75,1),
    'OLED_1p3_Module': (0.06,0.06,0.07,1), 'OLED_ActiveArea': (0.28,0.66,0.95,1),
    'LED_Diffuser_Ring': (0.55,0.80,0.97,1),
    'SG90_Fit_1': (0.40,0.58,0.86,1), 'SG90_Fit_2': (0.40,0.58,0.86,1),
    'SG90_Fit_3': (0.40,0.58,0.86,1), 'SG90_Fit_4': (0.40,0.58,0.86,1),
    'Touch_Module_Fit': (0.92,0.56,0.22,1),
    'PCB_Board': (0.10,0.40,0.22,1), 'PCB_Components': (0.20,0.56,0.30,1),
    'Battery_103450': (0.34,0.35,0.40,1), 'Speaker_3070': (0.52,0.52,0.55,1),
    'Button_Top_1': (0.97,0.97,0.94,1), 'Button_Top_2': (0.97,0.97,0.94,1),
    'Button_Top_3': (0.97,0.97,0.94,1),
    'Ear_R': (0.80,0.62,0.43,1), 'Ear_L': (0.80,0.62,0.43,1),
    'Tail': (0.80,0.62,0.43,1),
}
for n,c in COL.items():
    o = bpy.data.objects.get(n)
    if o: o.color = c

HIDE = {'Pet_Body_Blockout','V1_Base','V1_Lid','Cube','Preview_Ground'}
for n in HIDE:
    o = bpy.data.objects.get(n)
    if o: o.hide_render = True
for o in bpy.data.objects:
    if o.type in ('LIGHT','CAMERA'): o.hide_render = True
    if o.name.endswith('_Master'): o.hide_render = True

gm = bpy.data.meshes.new('GroundR'); g = bmesh.new()
bmesh.ops.create_grid(g, x_segments=1, y_segments=1, size=500)
g.to_mesh(gm); g.free()
ground = bpy.data.objects.new('GroundR', gm)
sc.collection.objects.link(ground)
ground.location.z = -0.06
ground.color = (0.13,0.13,0.15,1)

cam_d = bpy.data.cameras.new('CR'); cam = bpy.data.objects.new('CR', cam_d)
sc.collection.objects.link(cam); sc.camera = cam
cam_d.clip_start = 0.2; cam_d.clip_end = 5000
def look(t):
    cam.rotation_euler = (Vector(t)-cam.location).to_track_quat('-Z','Y').to_euler()
def shot(name, loc, target, mode='PERSP', lens=55, ortho=120, res=(1500,1500)):
    sc.render.resolution_x, sc.render.resolution_y = res
    cam.location = loc; look(target)
    if mode=='ORTHO':
        cam_d.type='ORTHO'; cam_d.ortho_scale=ortho
    else:
        cam_d.type='PERSP'; cam_d.lens=lens
    sc.render.filepath = os.path.join(OUT, name+'.png')
    bpy.ops.render.render(write_still=True)
    print('SHOT', name, flush=True)

def meshes():
    return [o for o in bpy.data.objects if o.type=='MESH' and not o.name.endswith('_Master')
            and o.name not in HIDE and o.name != 'GroundR']
def show_only(names):
    for o in meshes():
        o.hide_render = o.name not in names
def show_all(except_names=()):
    for o in meshes():
        o.hide_render = o.name in except_names

# ---------------- standard suite 30-41
show_all()
shot('30_rev3_hero', (215,235,150), (0,0,38), lens=55, res=(1700,1300))
ground.hide_render = True
shot('31_rev3_top', (0,0,320), (0,0,66), mode='ORTHO', ortho=150, res=(1400,1500))
shot('32_top_buttons', (-24.83,-42.45,190), (-24.83,-42.45,66), mode='ORTHO', ortho=32, res=(1400,1400))
shot('33_touch_grille', (0,35,190), (0,35,66), mode='ORTHO', ortho=26, res=(1400,1400))
ground.hide_render = False
shot('34_ears_front', (0,150,118), (0,22,70), lens=90, res=(1600,1250))
shot('35_tail_34', (-165,-215,145), (0,-46,76), lens=75, res=(1600,1500))
ground.hide_render = True
shot('36_tail_ring_side', (300,-46,77), (0,-46,77), mode='ORTHO', ortho=70, res=(1600,1300))
ground.hide_render = False

ground.hide_render = True
show_only({'Enclosure_Lid','Button_Top_1','Button_Top_2','Button_Top_3',
           'Ear_R','Ear_L','Tail','Touch_Module_Fit','LED_Diffuser_Ring'})
shot('37_lid_underside', (95,115,6), (0,0,63.5), lens=58, res=(1700,1400))
ground.hide_render = False
show_all()

MOVED = {'Button_Top_1':14,'Button_Top_2':14,'Button_Top_3':14,
         'Ear_R':20,'Ear_L':20,'Tail':22}
orig = {n: bpy.data.objects[n].location.copy() for n in MOVED}
for n,dz in MOVED.items():
    bpy.data.objects[n].location.z += dz
shot('38_exploded', (205,235,185), (0,-4,54), lens=52, res=(1700,1500))
for n,loc in orig.items():
    bpy.data.objects[n].location = loc
bpy.context.view_layer.update()

def cut_copy_boxes(names, boxes):
    objs=[]
    for n in names:
        o=bpy.data.objects[n]
        d=o.copy(); d.data=o.data.copy(); sc.collection.objects.link(d)
        d.hide_render=False
        for m in list(d.modifiers): d.modifiers.remove(m)
        objs.append(d)
    for center,size in boxes:
        cm=bpy.data.meshes.new('cutm'); bm=bmesh.new()
        bmesh.ops.create_cube(bm,size=1); bmesh.ops.scale(bm,vec=size,verts=bm.verts)
        bmesh.ops.translate(bm,vec=center,verts=bm.verts)
        bm.to_mesh(cm); bm.free()
        co=bpy.data.objects.new('cutobj',cm); sc.collection.objects.link(co)
        for d in objs:
            bpy.context.view_layer.objects.active=d
            md=d.modifiers.new('b','BOOLEAN'); md.operation='DIFFERENCE'; md.solver='MANIFOLD'; md.object=co
            bpy.ops.object.modifier_apply(modifier=md.name)
        bpy.data.objects.remove(co,do_unlink=True)
    return objs

# 39 button stub section
ground.hide_render=True
for o in meshes(): o.hide_render = True
btn_sec = cut_copy_boxes(['Enclosure_Lid','PCB_Board','PCB_Components','Button_Top_2'],
    [((-24.5-150,-42.45,62.0),(300,120,80)), ((-8+150,-42.45,62.0),(300,120,80))])
for d in btn_sec:
    d.hide_render = False
    d.color = COL.get(d.name.split('.')[0], (0.8,0.8,0.8,1))
shot('39_button_section', (-130,-42.45,62.2), (-24.5,-42.45,62.2), mode='ORTHO', ortho=14.0, res=(1600,1600))
for d in btn_sec: bpy.data.objects.remove(d, do_unlink=True)
show_all()

# 40 ear section
ground.hide_render=True
sec2 = cut_copy_boxes(['Enclosure_Lid','Ear_R'], [((21,180,70),(200,300,100))])
for o in meshes(): o.hide_render = True
for d in sec2:
    d.hide_render=False
    d.color = COL.get(d.name.split('.')[0], (0.8,0.8,0.8,1))
shot('40_ear_section', (21,140,72), (21,30,69), mode='ORTHO', ortho=28, res=(1400,1300))
for d in sec2: bpy.data.objects.remove(d, do_unlink=True)

# 41 tail section
ground.hide_render=True
sec3 = cut_copy_boxes(['Enclosure_Lid','Tail'],
    [((0-150,-43,73),(300,150,100)), ((10+150,-43,73),(300,150,100))])
for o in meshes(): o.hide_render = True
for d in sec3:
    d.hide_render=False
    d.color = COL.get(d.name.split('.')[0], (0.8,0.8,0.8,1))
shot('41_tail_section', (-140,-43,77.0), (0,-43,77.0), mode='ORTHO', ortho=40, res=(1400,1500))
for d in sec3: bpy.data.objects.remove(d, do_unlink=True)

# ---------------- 42-48 internal structure set
show_all()
ground.hide_render = True

shot('42_int_buttons_top', (-24.83,-42.45,190), (-24.83,-42.45,66), mode='ORTHO', ortho=26, res=(1400,1400))
shot('43_int_buttons_34', (-95,-100,96), (-24.8,-42.5,66.4), lens=90, res=(1700,1400))

for o in meshes(): o.hide_render = True
show_only({'Enclosure_Lid','Button_Top_1','Button_Top_2','Button_Top_3'})
sh.studiolight_rotate_z = math.radians(200)
shot('44_int_lid_under', (-85,-105,26), (-20,-42,63.4), lens=70, res=(1600,1450))
sh.studiolight_rotate_z = 0.0

for o in meshes(): o.hide_render = True
show_only({'PCB_Board','PCB_Components','OLED_1p3_Module','OLED_ActiveArea',
           'SG90_Fit_1','SG90_Fit_2','SG90_Fit_3','SG90_Fit_4',
           'Battery_103450','Speaker_3070','Touch_Module_Fit',
           'Leg_L','Leg_R','Leg_L_Rear','Leg_R_Rear'})
shot('45_int_deck_34', (190,-210,150), (0,-5,42), lens=55, res=(1700,1400))

for o in meshes(): o.hide_render = True
show_only({'PCB_Board','PCB_Components','OLED_1p3_Module','OLED_ActiveArea',
           'SG90_Fit_1','SG90_Fit_2','SG90_Fit_3','SG90_Fit_4',
           'Battery_103450','Speaker_3070'})
shot('46_int_deck_top', (0,0,320), (0,0,40), mode='ORTHO', ortho=135, res=(1500,1500))

for o in meshes(): o.hide_render = True
sec4 = cut_copy_boxes(['Enclosure_Body','Enclosure_Lid','LED_Diffuser_Ring','Face_Plate','Belly_Pan',
                       'PCB_Board','PCB_Components','Battery_103450','Speaker_3070',
                       'OLED_1p3_Module','OLED_ActiveArea','SG90_Fit_1','SG90_Fit_2',
                       'SG90_Fit_3','SG90_Fit_4','Touch_Module_Fit',
                       'Leg_L','Leg_R','Leg_L_Rear','Leg_R_Rear'],
                      [((0+150,-10,50),(300,300,200))])
for d in sec4:
    d.hide_render = False
    d.color = COL.get(d.name.split('.')[0], (0.8,0.8,0.8,1))
shot('47_int_cutaway_x', (210,150,130), (0,-10,45), lens=55, res=(1700,1400))

for d in sec4: bpy.data.objects.remove(d, do_unlink=True)
show_all()
for o in meshes(): o.hide_render = True
btn_sec2 = cut_copy_boxes(['Enclosure_Lid','PCB_Board','PCB_Components','Button_Top_2'],
    [((-24.5-150,-42.45,62.0),(300,120,80)), ((-8+150,-42.45,62.0),(300,120,80))])
for d in btn_sec2:
    d.hide_render = False
    d.color = COL.get(d.name.split('.')[0], (0.8,0.8,0.8,1))
shot('48_int_button_section_34', (-115,-95,92), (-24.5,-42.4,62.2), lens=75, res=(1600,1500))
for d in btn_sec2: bpy.data.objects.remove(d, do_unlink=True)
print('ALL DONE', flush=True)
