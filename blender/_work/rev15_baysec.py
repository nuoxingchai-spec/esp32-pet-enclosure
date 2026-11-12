import bpy, bmesh, math, os
from mathutils import Vector
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
OUT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_review"
bpy.ops.wm.open_mainfile(filepath=BLEND)
sc=bpy.context.scene; sh=sc.display.shading
sc.render.engine='BLENDER_WORKBENCH'; sh.light='STUDIO'; sh.color_type='OBJECT'; sh.show_cavity=True; sh.cavity_type='BOTH'
sh.show_shadows=True; sc.world.color=(0.045,0.045,0.055); sc.view_settings.view_transform='Standard'
COL={'Enclosure_Body':(0.84,0.84,0.82,1),'SG90_Fit_1':(0.40,0.58,0.86,1),'SG90_Fit_2':(0.40,0.58,0.86,1),
     'SG90_Fit_3':(0.40,0.58,0.86,1),'SG90_Fit_4':(0.40,0.58,0.86,1),'Leg_R':(0.96,0.91,0.83,1),'Leg_L':(0.96,0.91,0.83,1)}
for n,c in COL.items():
    o=bpy.data.objects.get(n)
    if o: o.color=c
for o in bpy.data.objects:
    if o.type in ('LIGHT','CAMERA'): o.hide_render=True
    if o.name.endswith('_Master'): o.hide_render=True
meshes=[o for o in bpy.data.objects if o.type=='MESH']
cam_d=bpy.data.cameras.new('CR'); cam=bpy.data.objects.new('CR',cam_d); sc.collection.objects.link(cam); sc.camera=cam
cam_d.clip_start=0.2; cam_d.clip_end=5000
def shot(name,loc,target,mode='ORTHO',ortho=60,lens=55,res=(1600,1400)):
    sc.render.resolution_x,sc.render.resolution_y=res
    cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    if mode=='ORTHO': cam_d.type='ORTHO'; cam_d.ortho_scale=ortho
    else: cam_d.type='PERSP'; cam_d.lens=lens
    sc.render.filepath=os.path.join(OUT,name+'.png'); bpy.ops.render.render(write_still=True); print('SHOT',name)
def cut_copy(names,boxes,keep=None):
    objs=[]
    for n in names:
        o=bpy.data.objects[n]; d=o.copy(); d.data=o.data.copy(); sc.collection.objects.link(d)
        d.hide_render=False
        for m in list(d.modifiers): d.modifiers.remove(m)
        objs.append(d)
    for center,size in boxes:
        cm=bpy.data.meshes.new('cutm'); bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1); bmesh.ops.scale(bm,vec=size,verts=bm.verts); bmesh.ops.translate(bm,vec=center,verts=bm.verts)
        bm.to_mesh(cm); bm.free(); co=bpy.data.objects.new('cutobj',cm); sc.collection.objects.link(co)
        for d in objs:
            bpy.context.view_layer.objects.active=d
            md=d.modifiers.new('b','BOOLEAN'); md.operation='DIFFERENCE'; md.solver='MANIFOLD'; md.object=co
            bpy.ops.object.modifier_apply(modifier=md.name)
        bpy.data.objects.remove(co,do_unlink=True)
    return objs
# section at y=44 (front servo center)
sec=cut_copy(['Enclosure_Body','SG90_Fit_1','SG90_Fit_3','Leg_L','Leg_R'],
             [((0,44-150,45),(400,300,200)),((0,44+150,45),(400,300,200))])
for o in meshes: o.hide_render=True
for d in sec:
    d.hide_render=False; d.color=COL.get(d.name.split('.')[0],(0.8,0.8,0.8,1))
shot('49_bay_section_y44',(230,44,44),(0,44,44),ortho=70,res=(1800,1400))
for d in sec: bpy.data.objects.remove(d,do_unlink=True)
# top section z=40: remove above 40
sec2=cut_copy(['Enclosure_Body','SG90_Fit_1','SG90_Fit_2','SG90_Fit_3','SG90_Fit_4','Leg_L','Leg_R','Leg_L_Rear','Leg_R_Rear'],
              [((0,0,40+80),(400,400,160))])
for o in meshes: o.hide_render=True
for d in sec2:
    d.hide_render=False; d.color=COL.get(d.name.split('.')[0],(0.8,0.8,0.8,1))
shot('50_bay_section_z40',(0,0,260),(0,0,40),ortho=150,res=(1600,1500))
for d in sec2: bpy.data.objects.remove(d,do_unlink=True)
# list horizontal faces in bay
body=bpy.data.objects['Enclosure_Body']; bm=bmesh.new(); bm.from_mesh(body.data); bm.transform(body.matrix_world)
zs={}
for f in bm.faces:
    c=f.calc_center_median()
    if 13<c.x<37 and 26<c.y<61 and f.normal.z>0.7 and 39<c.z<56:
        zs.setdefault(round(c.z,2),[]).append((round(c.x,1),round(c.y,1)))
for z in sorted(zs): print('upface z',z,'n',len(zs[z]),'sample',zs[z][:6])
bm.free()
