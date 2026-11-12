import bpy, math
from mathutils import Vector, Matrix
F = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev4_test_lift.blend"
bpy.ops.wm.open_mainfile(filepath=F)
sc = bpy.context.scene
mod = bpy.data.objects['BODY_TEST']
orig = bpy.data.objects['Enclosure_Body']
mod.matrix_world = Matrix.Identity(4)   # its mesh was written in world coords
for o in sc.objects:
    if o.type == 'MESH' and o.name not in ('BODY_TEST','Enclosure_Body'):
        o.hide_render = True
    if o.type == 'MESH':
        o.hide_viewport = True
orig.hide_viewport = False

sc.render.engine='BLENDER_WORKBENCH'
sh=sc.display.shading
sh.light='STUDIO'; sh.studio_light='Default'; sh.color_type='OBJECT'
sh.show_cavity=True; sh.cavity_type='BOTH'; sh.curvature_ridge_factor=2.0; sh.curvature_valley_factor=2.0
sh.show_shadows=True; sh.shadow_intensity=0.35
sc.world.color=(0.82,0.85,0.9)
sc.render.resolution_x=1100; sc.render.resolution_y=900
sc.render.image_settings.file_format='PNG'
cam = bpy.data.objects.get('C'); sc.camera = cam

def look(pos, tgt, lens=70):
    cam.location=pos; cam.data.lens=lens
    d=Vector(tgt)-Vector(pos); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
def shot(p):
    sc.render.filepath=p; bpy.ops.render.render(write_still=True)

VIEWS = [
    ('q', (150,-120,80), (36,-58,47), 80),
    ('s', (170,-62,50), (39,-58,50), 75),
    ('t', (86,-70,120), (36.5,-58,53), 70),
]
for tag, pos, tgt, lens in VIEWS:
    look(pos,tgt,lens)
    orig.hide_render=False; mod.hide_render=True
    shot(rf"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\ab2_orig_{tag}.png")
    orig.hide_render=True; mod.hide_render=False
    shot(rf"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\ab2_new_{tag}.png")
print('DONE')
