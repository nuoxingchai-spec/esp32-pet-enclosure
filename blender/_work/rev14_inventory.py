import bpy
from mathutils import Vector

BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)

def wb(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (min(p.x for p in pts), max(p.x for p in pts),
            min(p.y for p in pts), max(p.y for p in pts),
            min(p.z for p in pts), max(p.z for p in pts))

print("=== OBJECTS ===")
for o in sorted(bpy.data.objects, key=lambda x: x.name):
    if o.type == 'MESH':
        x0, x1, y0, y1, z0, z1 = wb(o)
        print(f"{o.name:28s} {o.type:6s} col={[c.name for c in o.users_collection]} "
              f"bb=({x0:.2f},{x1:.2f})({y0:.2f},{y1:.2f})({z0:.2f},{z1:.2f}) "
              f"dims=({o.dimensions.x:.2f},{o.dimensions.y:.2f},{o.dimensions.z:.2f}) "
              f"loc=({o.location.x:.2f},{o.location.y:.2f},{o.location.z:.2f}) "
              f"hide={o.hide_render}")
    else:
        print(f"{o.name:28s} {o.type:6s} col={[c.name for c in o.users_collection]} loc={tuple(round(v,2) for v in o.location)}")
print("=== COLLECTIONS ===")
for c in bpy.data.collections:
    print(c.name, len(c.objects), [o.name for o in c.objects][:50])
print("=== DATA MESHES ===")
for m in bpy.data.meshes:
    print(m.name, len(m.vertices), len(m.polygons), m.users)
