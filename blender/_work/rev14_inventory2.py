import bpy
from mathutils import Vector
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
for o in sorted(bpy.context.scene.objects, key=lambda o:o.name):
    if o.type!='MESH': continue
    b=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[p.x for p in b]; ys=[p.y for p in b]; zs=[p.z for p in b]
    print(f"{o.name:24s} x[{min(xs):7.2f},{max(xs):7.2f}] y[{min(ys):7.2f},{max(ys):7.2f}] z[{min(zs):7.2f},{max(zs):7.2f}]  coll={o.users_collection[0].name}")
