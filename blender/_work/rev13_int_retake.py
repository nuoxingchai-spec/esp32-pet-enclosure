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
    'Enclosure_Lid': (0.76,0.76,0.74,1),
    'LED_Diffuser_Ring': (0.55,0.80,0.97,1),
    'Button_Top_1': (0.97,0.97,0.94,1), 'Button_Top_2': (0.97,0.97,0.94,1),
    'Button_Top_3': (0.97,0.97,0.94,1),
    'PCB_Board': (0.10,0.40,0.22,1), 'PCB_Components': (0.20,0.56,0.30,1),
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
            and o.name not in HIDE]
def show_only(names):
    for o in meshes():
        o.hide_render = o.name not in names

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

# 42 straight top, tight crop
for o in meshes(): o.hide_render = True
show_only({'Enclosure_Lid','Button_Top_1','Button_Top_2','Button_Top_3'})
shot('42_int_buttons_top', (-24.83,-42.45,190), (-24.83,-42.45,66), mode='ORTHO', ortho=22, res=(1500,1400))

# 43 low 3/4 along the row
shot('43_int_buttons_34', (-78,-18,96), (-24.8,-42.5,67.0), lens=100, res=(1700,1400))

# 48 section 3/4, tighter
for o in meshes(): o.hide_render = True
btn_sec2 = cut_copy_boxes(['Enclosure_Lid','PCB_Board','PCB_Components','Button_Top_2'],
    [((-24.5-150,-42.45,62.0),(300,120,80)), ((-8+150,-42.45,62.0),(300,120,80))])
for d in btn_sec2:
    d.hide_render = False
    d.color = COL.get(d.name.split('.')[0], (0.8,0.8,0.8,1))
shot('48_int_button_section_34', (-95,-72,82), (-24.5,-42.4,62.4), lens=100, res=(1600,1500))
print('ALL DONE', flush=True)
