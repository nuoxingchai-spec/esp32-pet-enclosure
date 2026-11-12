import bpy, bmesh, math, os
from mathutils import Vector

ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
OUT = os.path.join(ROOT, r"blender\_work")
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT, 'rev13_smooth.blend'))
sc = bpy.context.scene
lid = bpy.data.objects['Enclosure_Lid']

bm = bmesh.new(); bm.from_mesh(lid.data)
loose = [e for e in bm.edges if not e.link_faces]
print('loose edges', len(loose))
bmesh.ops.delete(bm, geom=loose, context='EDGES')
loosev = [v for v in bm.verts if not v.link_faces]
if loosev:
    bmesh.ops.delete(bm, geom=loosev, context='VERTS')
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(lid.data); bm.free()
lid.data.update()
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()

bm = bmesh.new(); bm.from_mesh(lid.data)
print(f"LID AUDIT v={len(bm.verts)} f={len(bm.faces)} "
      f"nm={sum(1 for e in bm.edges if len(e.link_faces) != 2)} "
      f"bnd={sum(1 for e in bm.edges if len(e.link_faces) < 2)} "
      f"zero={sum(1 for f in bm.faces if f.calc_area() < 1e-9)} vol={bm.calc_volume(signed=True):.2f}")
bm.free()

# ------------------------------------------------------------- render setup
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading
sh.light = 'STUDIO'; sh.studio_light = 'Default'; sh.color_type = 'OBJECT'
sh.show_cavity = True; sh.cavity_type = 'BOTH'
sh.curvature_ridge_factor = 1.0; sh.curvature_valley_factor = 1.0
sh.show_shadows = True; sh.shadow_intensity = 0.5
sh.show_object_outline = False
sc.world.color = (0.045, 0.045, 0.055)
sc.render.image_settings.file_format = 'PNG'
sc.view_settings.view_transform = 'Standard'
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
    'Ear_R': (0.80,0.62,0.43,1), 'Ear_L': (0.80,0.62,0.43,1), 'Tail': (0.80,0.62,0.43,1),
}
for n, c in COL.items():
    o = bpy.data.objects.get(n)
    if o: o.color = c
HIDE = {'Pet_Body_Blockout','V1_Base','V1_Lid','Cube','Preview_Ground'}
for n in HIDE:
    o = bpy.data.objects.get(n)
    if o: o.hide_render = True
for o in bpy.data.objects:
    if o.type in ('LIGHT','CAMERA'): o.hide_render = True
    if o.name.endswith('_Master'): o.hide_render = True

cam_d = bpy.data.cameras.new('C'); cam = bpy.data.objects.new('C', cam_d)
sc.collection.objects.link(cam); sc.camera = cam
cam_d.clip_start = 0.2; cam_d.clip_end = 5000
def look(pos, tgt, lens=55):
    cam.location = pos; cam_data = cam.data
    cam.rotation_euler = (Vector(tgt) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
def shot(name, loc, tgt, lens=55, ortho=None, res=(1500,1500)):
    sc.render.resolution_x, sc.render.resolution_y = res
    cam.location = loc; look(loc, tgt)
    if ortho:
        cam.data.type = 'ORTHO'; cam.data.ortho_scale = ortho
    else:
        cam.data.type = 'PERSP'; cam.data.lens = lens
    sc.render.filepath = os.path.join(OUT, name + '.png')
    bpy.ops.render.render(write_still=True)
    print('SHOT', name, flush=True)

def meshes():
    return [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.endswith('_Master')
            and o.name not in HIDE]
def show_only(names):
    for o in meshes():
        o.hide_render = o.name not in names
def show_all(except_names=()):
    for o in meshes():
        o.hide_render = o.name in except_names

def cut_copy_boxes(names, boxes):
    objs = []
    for n in names:
        o = bpy.data.objects[n]
        d = o.copy(); d.data = o.data.copy(); sc.collection.objects.link(d)
        d.hide_render = False
        for m in list(d.modifiers): d.modifiers.remove(m)
        objs.append(d)
    for center, size in boxes:
        cm = bpy.data.meshes.new('cutm'); bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=size, verts=bm.verts)
        bmesh.ops.translate(bm, vec=center, verts=bm.verts)
        bm.to_mesh(cm); bm.free()
        co = bpy.data.objects.new('cutobj', cm); sc.collection.objects.link(co)
        for d in objs:
            bpy.context.view_layer.objects.active = d
            md = d.modifiers.new('b', 'BOOLEAN'); md.operation = 'DIFFERENCE'
            md.solver = 'MANIFOLD'; md.object = co
            bpy.ops.object.modifier_apply(modifier=md.name)
        bpy.data.objects.remove(co, do_unlink=True)
    return objs

# --- 1. button section (slab x -24.5..-8)
show_all()
for o in meshes(): o.hide_render = True
sec = cut_copy_boxes(['Enclosure_Lid','PCB_Board','PCB_Components','Button_Top_2'],
                     [((-24.5-150,-42.45,62.0),(300,120,80)), ((-8+150,-42.45,62.0),(300,120,80))])
for d in sec:
    d.hide_render = False
    d.color = COL.get(d.name.split('.')[0], (0.8,0.8,0.8,1))
shot('test_button_section', (-130,-42.45,62.2), (-24.5,-42.45,62.2), ortho=14.0, res=(1600,1600))
for d in sec: bpy.data.objects.remove(d, do_unlink=True)
show_all()

# --- 2. lid underside close-up on buttons
for o in meshes(): o.hide_render = True
show_only({'Enclosure_Lid','Button_Top_1','Button_Top_2','Button_Top_3'})
shot('test_lid_buttons_under', (-85,-105,30), (-20,-42,63), lens=70, res=(1600,1400))

# --- 3. internals only (no shell)
for o in meshes(): o.hide_render = True
show_only({'PCB_Board','PCB_Components','OLED_1p3_Module','OLED_ActiveArea',
           'SG90_Fit_1','SG90_Fit_2','SG90_Fit_3','SG90_Fit_4',
           'Battery_103450','Speaker_3070','Touch_Module_Fit',
           'Leg_L','Leg_R','Leg_L_Rear','Leg_R_Rear'})
shot('test_internals_deck', (190,-210,150), (0,-5,42), lens=55, res=(1700,1400))

# --- 4. half cutaway at x=0, shell + internals cut
for o in meshes(): o.hide_render = True
sec2 = cut_copy_boxes(['Enclosure_Body','Enclosure_Lid','LED_Diffuser_Ring','Face_Plate','Belly_Pan',
                       'PCB_Board','PCB_Components','Battery_103450','Speaker_3070',
                       'OLED_1p3_Module','OLED_ActiveArea','SG90_Fit_1','SG90_Fit_2',
                       'SG90_Fit_3','SG90_Fit_4','Touch_Module_Fit',
                       'Leg_L','Leg_R','Leg_L_Rear','Leg_R_Rear'],
                      [((0+150,-10,50),(300,300,200))])
for d in sec2:
    d.hide_render = False
    d.color = COL.get(d.name.split('.')[0], (0.8,0.8,0.8,1))
shot('test_cutaway_x', (210,150,130), (0,-10,45), lens=55, res=(1700,1400))
for d in sec2: bpy.data.objects.remove(d, do_unlink=True)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'rev13_smooth.blend'))
print('SAVED')
print('DONE')
