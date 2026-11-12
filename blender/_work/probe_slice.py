import bpy, math
from mathutils import Vector
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
sc=bpy.context.scene
sc.render.engine='BLENDER_WORKBENCH'
sh=sc.display.shading
sh.light='STUDIO'; sh.studio_light='Default'; sh.color_type='OBJECT'
sh.show_cavity=True; sh.cavity_type='BOTH'
sh.curvature_ridge_factor=2.0; sh.curvature_valley_factor=2.0
sh.show_shadows=True; sh.shadow_intensity=0.3
sc.world.color=(0.75,0.78,0.82)
sc.render.resolution_x=1000; sc.render.resolution_y=1400
sc.render.image_settings.file_format='PNG'
bpy.data.objects['Preview_Ground'].hide_render=True
names=['Enclosure_Body','Enclosure_Lid','Leg_R','SG90_Fit_1']
keep=[]
for n in names:
    o=bpy.data.objects.get(n)
    if o: keep.append(o)
for o in bpy.data.objects:
    if o.type=='MESH' and o not in keep: o.hide_render=True
# colors
for o in keep:
    o.color=(0.75,0.78,0.82,1) if o.name.startswith('Enclosure') else ((0.85,0.72,0.52,1) if o.name.startswith('Leg') else (0.25,0.45,0.75,1))
def cut_slab(o,z0,z1):
    c=o.copy(); c.data=o.data.copy(); sc.collection.objects.link(c); c.hide_render=False
    bpy.ops.mesh.primitive_cube_add(size=1, location=((30+55)/2,(20+65)/2,(z0+z1)/2))
    cut=bpy.context.object; cut.name='CUT'; cut.scale=(25,45,z1-z0)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.context.view_layer.objects.active=c; c.select_set(True)
    m=c.modifiers.new('b','BOOLEAN'); m.operation='INTERSECT'; m.solver='MANIFOLD'; m.object=cut
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cut,do_unlink=True)
    return c
slabs=[]
for o in keep:
    if o.name=='Enclosure_Lid': continue
    slabs.append(cut_slab(o,41.5,42.5))
    o.hide_render=True
cam_d=bpy.data.cameras.new('C'); cam=bpy.data.objects.new('C',cam_d); sc.collection.objects.link(cam); sc.camera=cam
cam_d.type='ORTHO'; cam_d.ortho_scale=52
cam.location=(40,43,160); cam.rotation_euler=(0,0,0)
sc.render.filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\slice_z42.png"
bpy.ops.render.render(write_still=True)
cam_d.type='PERSP'; cam_d.lens=85
cam.location=(95,80,105); d=Vector((42,43,42))-Vector(cam.location); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
sc.render.filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\slice_z42_persp.png"
bpy.ops.render.render(write_still=True)
print('done')
