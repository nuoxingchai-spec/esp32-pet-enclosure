import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend')
dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['Enclosure_Body']; ev=o.evaluated_get(dg); mw=o.matrix_world; inv=mw.inverted()
print('shading xray', bpy.context.scene.display.shading.show_xray)
for y in (-50,-30,-10,0,10,30,50):
    for z in (30,40,50):
        ok,loc,nor,idx=ev.ray_cast(inv@Vector((50,y,z)),(inv.to_3x3()@Vector((-1,0,0))).normalized(),distance=200)
        p=mw@loc if ok else None
        print(f'({y},{z}) -> {tuple(round(v,2) for v in p) if p else None}')
