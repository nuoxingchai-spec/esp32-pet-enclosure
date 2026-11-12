import bpy, bmesh, math, os
from mathutils import Vector

OUT = r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_review'
bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend")
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
scene.world.color = (0.045, 0.045, 0.055)

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
scene.collection.objects.link(ground)
ground.location.z = -0.06
ground.color = (0.13,0.13,0.15,1)

cam_data = bpy.data.cameras.new('CR'); cam = bpy.data.objects.new('CR', cam_data)
scene.collection.objects.link(cam); scene.camera = cam
cam_data.clip_start = 0.2; cam_data.clip_end = 5000

def look(t): cam.rotation_euler = (Vector(t)-cam.location).to_track_quat('-Z','Y').to_euler()

def meshes():
    return [o for o in bpy.data.objects if o.type=='MESH' and not o.name.endswith('_Master')
            and o.name not in HIDE and o.name != 'GroundR']

def show_only(names):
    for o in meshes():
        o.hide_render = o.name not in names

def show_all(except_names=()):
    for o in meshes():
        o.hide_render = o.name in except_names

def shot(name, loc, target, mode='PERSP', lens=55, ortho=120, res=(1500,1500)):
    scene.render.resolution_x, scene.render.resolution_y = res
    cam.location = loc; look(target)
    if mode=='ORTHO':
        cam_data.type='ORTHO'; cam_data.ortho_scale=ortho
    else:
        cam_data.type='PERSP'; cam_data.lens=lens
    scene.render.filepath = os.path.join(OUT, name+'.png')
    bpy.ops.render.render(write_still=True)
    print('SHOT', name, flush=True)

show_all()
shot('30_rev3_hero', (215,235,150), (0,0,38), lens=55, res=(1700,1300))
ground.hide_render = True
shot('31_rev3_top', (0,0,320), (0,0,66), mode='ORTHO', ortho=150, res=(1400,1500))
shot('32_top_buttons', (-24.83,-42.45,190), (-24.83,-42.45,66), mode='ORTHO', ortho=32, res=(1400,1400))
shot('33_touch_grille', (0,35,190), (0,35,66), mode='ORTHO', ortho=26, res=(1400,1400))
ground.hide_render = False
shot('34_ears_front', (0,150,118), (0,22,70), lens=90, res=(1600,1250))
shot('35_tail_34', (-150,-195,125), (0,-48,72), lens=80, res=(1600,1300))
ground.hide_render = True
shot('36_tail_ring_side', (300,-48,73), (0,-48,73), mode='ORTHO', ortho=58, res=(1600,1200))
ground.hide_render = False

# lid underside with all add-ons
ground.hide_render = True
show_only({'Enclosure_Lid','Button_Top_1','Button_Top_2','Button_Top_3',
           'Ear_R','Ear_L','Tail','Touch_Module_Fit','LED_Diffuser_Ring'})
shot('37_lid_underside', (95,115,6), (0,0,63.5), lens=58, res=(1700,1400))
ground.hide_render = False
show_all()

# exploded view: temporarily lift detachables
MOVED = {'Button_Top_1':14,'Button_Top_2':14,'Button_Top_3':14,
         'Ear_R':20,'Ear_L':20,'Tail':22}
orig = {n: bpy.data.objects[n].location.copy() for n in MOVED}
for n,dz in MOVED.items():
    bpy.data.objects[n].location.z += dz
shot('38_exploded', (190,220,165), (0,-2,48), lens=55, res=(1700,1400))
for n,loc in orig.items():
    bpy.data.objects[n].location = loc
bpy.context.view_layer.update()

# ---------- helper for section cuts ----------
def cut_copy(names, box_center, box_size, label):
    objs=[]
    for n in names:
        o=bpy.data.objects[n]
        d=o.copy(); d.data=o.data.copy(); scene.collection.objects.link(d)
        d.hide_render=False
        for m in list(d.modifiers): d.modifiers.remove(m)
        objs.append(d)
    cm=bpy.data.meshes.new('cutm'); bm=bmesh.new()
    bmesh.ops.create_cube(bm,size=1); bmesh.ops.scale(bm,vec=box_size,verts=bm.verts)
    bmesh.ops.translate(bm,vec=box_center,verts=bm.verts)
    bm.to_mesh(cm); bm.free()
    co=bpy.data.objects.new('cutobj',cm); scene.collection.objects.link(co)
    for d in objs:
        bpy.context.view_layer.objects.active=d
        md=d.modifiers.new('b','BOOLEAN'); md.operation='DIFFERENCE'; md.solver='MANIFOLD'; md.object=co
        bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(co,do_unlink=True)
    return objs

def cut_copy_boxes(names, boxes):
    objs=[]
    for n in names:
        o=bpy.data.objects[n]
        d=o.copy(); d.data=o.data.copy(); scene.collection.objects.link(d)
        d.hide_render=False
        for m in list(d.modifiers): d.modifiers.remove(m)
        objs.append(d)
    for center,size in boxes:
        cm=bpy.data.meshes.new('cutm'); bm=bmesh.new()
        bmesh.ops.create_cube(bm,size=1); bmesh.ops.scale(bm,vec=size,verts=bm.verts)
        bmesh.ops.translate(bm,vec=center,verts=bm.verts)
        bm.to_mesh(cm); bm.free()
        co=bpy.data.objects.new('cutobj',cm); scene.collection.objects.link(co)
        for d in objs:
            bpy.context.view_layer.objects.active=d
            md=d.modifiers.new('b','BOOLEAN'); md.operation='DIFFERENCE'; md.solver='MANIFOLD'; md.object=co
            bpy.ops.object.modifier_apply(modifier=md.name)
        bpy.data.objects.remove(co,do_unlink=True)
    return objs

# button mechanism section: slab x=-24.83..-10
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

# ear mount section at y=30
ground.hide_render=True
sec2 = cut_copy(['Enclosure_Lid','Ear_R'], box_center=(21,30+150,70), box_size=(200,300,100), label='ear')
for o in meshes(): o.hide_render = True
for d in sec2:
    d.hide_render=False
    d.color = COL.get(d.name.split('.')[0], (0.8,0.8,0.8,1))
shot('40_ear_section', (21,140,72), (21,30,69), mode='ORTHO', ortho=28, res=(1400,1300))
for d in sec2: bpy.data.objects.remove(d, do_unlink=True)

# tail mount section: slab x=0..10
sec3 = cut_copy_boxes(['Enclosure_Lid','Tail'],
    [((0-150,-43,73),(300,150,100)), ((10+150,-43,73),(300,150,100))])
for o in meshes(): o.hide_render = True
for d in sec3:
    d.hide_render=False
    d.color = COL.get(d.name.split('.')[0], (0.8,0.8,0.8,1))
shot('41_tail_section', (-140,-43,73.5), (0,-43,73.5), mode='ORTHO', ortho=30, res=(1400,1500))
for d in sec3: bpy.data.objects.remove(d, do_unlink=True)

print('ALL DONE', flush=True)
