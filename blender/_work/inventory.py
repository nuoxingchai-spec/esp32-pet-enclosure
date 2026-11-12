import bpy
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
for o in bpy.context.scene.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world @ __import__('mathutils').Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    print(f"{o.name:22s} v={len(o.data.vertices):5d} x[{min(xs):7.2f},{max(xs):7.2f}] y[{min(ys):7.2f},{max(ys):7.2f}] z[{min(zs):6.2f},{max(zs):6.2f}] hide={o.hide_viewport}/{o.hide_render}")
