import bpy, json
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world @ __import__('mathutils').Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    print("%-22s loc(%7.2f,%7.2f,%7.2f) bbox x[%7.2f,%7.2f] y[%7.2f,%7.2f] z[%7.2f,%7.2f] verts %d"%(
        o.name,o.location.x,o.location.y,o.location.z,min(xs),max(xs),min(ys),max(ys),min(zs),max(zs),len(o.data.vertices)))
