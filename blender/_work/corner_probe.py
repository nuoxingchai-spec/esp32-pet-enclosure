import bpy, math
from mathutils import Vector
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob=bpy.data.objects['Enclosure_Body']; mw=ob.matrix_world; mi=mw.inverted()
dg=bpy.context.evaluated_depsgraph_get()
def hx(side,y,z):
    org=mi@Vector((60.0*side,y,z)); d=(mw.to_3x3().inverted()@Vector((-side,0,0))).normalized()
    ok,loc,nor,idx=ob.ray_cast(org,d,distance=200.0,depsgraph=dg)
    return None if not ok else (mw@loc).x
print('== step z at side wall y=-60/+60 ==')
for side in (1,-1):
    for ya in (-60,60):
        prev=None; jumps=[]
        z=52.0
        while z<=57.0:
            x=hx(side,ya,z)
            if x is not None:
                xx=round(side*x,3)
                if prev is not None and abs(xx-prev)>0.3:
                    jumps.append((round(z,2),prev,xx))
                prev=xx
            z+=0.05
        print(f'side={side:+d} y={ya:+d} jumps={jumps}')
print('== corner flat span (last y with |x|>=38.9), z52 vs z56 ==')
for side in (1,-1):
    for z in (52,56,58.5):
        ends=[]
        for ya in (-64,-60,-58,-56,56,58,60,64):
            x=hx(side,ya,z)
            ends.append((ya, None if x is None else round(side*x,2)))
        print(f'side={side:+d} z={z}: {ends}')
print('== side wall anchors ==')
for p in [(1,-55,52),(1,-60,52),(1,-60,56),(1,55,56),(1,60,56),(-1,-60,52),(-1,-60,56),(-1,60,56)]:
    x=hx(*p); print(p, None if x is None else round(x,3))
print('== hip refs ==')
for n in ['Leg_R_Rear','Leg_R']:
    o=bpy.data.objects[n]
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    print(n,'y',round(min(v.y for v in vs),2),round(max(v.y for v in vs),2),'zmax',round(max(v.z for v in vs),2))
# renders
sc=bpy.context.scene
sc.render.engine='BLENDER_WORKBENCH'
sh=sc.display.shading
sh.light='STUDIO'; sh.studio_light='Default'; sh.color_type='OBJECT'
sh.show_cavity=True; sh.cavity_type='BOTH'
sh.curvature_ridge_factor=2.0; sh.curvature_valley_factor=2.0
sh.show_shadows=True; sh.shadow_intensity=0.35
sc.world.color=(0.82,0.85,0.9)
sc.render.resolution_x=900; sc.render.resolution_y=1000
sc.render.image_settings.file_format='PNG'
bpy.data.objects['Preview_Ground'].hide_render=True
for n in ['Enclosure_Lid','LED_Diffuser_Ring','Ear_L','Ear_R','Tail']:
    o=bpy.data.objects.get(n)
    if o: o.hide_render=True
cam_d=bpy.data.cameras.new('C'); cam=bpy.data.objects.new('C',cam_d); sc.collection.objects.link(cam); sc.camera=cam
def look(pos,tgt,lens):
    cam.location=pos; d=Vector(tgt)-Vector(pos); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); cam_d.lens=lens
def shot(name):
    sc.render.filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\\"+name
    bpy.ops.render.render(write_still=True)
look((120,-58,47),(39,-57,40),85); shot('edge_context.png')
for o in bpy.data.objects:
    if o.name.startswith('Leg_'): o.hide_render=True
look((82,-66,51),(38.8,-60.3,47.5),110); shot('edge_close.png')
look((62,-46,66),(38.8,-59.5,53.8),85); shot('edge_step.png')
print('done')
