import bpy
from mathutils import Vector
print("FILE", bpy.data.filepath)
for o in sorted(bpy.data.objects, key=lambda x: x.name):
    if o.type != 'MESH': continue
    t = o.matrix_world.translation
    print(f"HV {o.name:22s} hide_viewport={o.hide_viewport} hide_get={o.hide_get()} hide_render={o.hide_render} loc_z={o.location.z:7.3f} mwt_z={t.z:7.3f}")
