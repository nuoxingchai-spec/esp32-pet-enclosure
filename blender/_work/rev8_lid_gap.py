import bpy, math
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend")
dg = bpy.context.evaluated_depsgraph_get()

print("OBJECTS:", [(o.name, o.type) for o in bpy.data.objects])

def hits(name, org, d):
    ob = bpy.data.objects[name]
    mw = ob.matrix_world
    m3i = mw.to_3x3().inverted()
    o = mw.inverted() @ Vector(org)
    dd = (m3i @ Vector(d)).normalized()
    out = []
    p = o.copy()
    for i in range(8):
        ok, loc, nor, idx = ob.ray_cast(p, dd, distance=500, depsgraph=dg)
        if not ok:
            break
        w = mw @ loc
        out.append((round(w.x, 4), round(w.y, 4), round(w.z, 4), round(nor.x, 3), round(nor.z, 3)))
        p = loc + dd * 0.003
    return out

for z in (58.5, 59.0, 59.5):
    for y in (-30, -45, -50, 0, 30):
        b = hits("Enclosure_Body", (60, y, z), (-1, 0, 0))
        l = hits("Enclosure_Lid", (60, y, z), (-1, 0, 0))
        print(f"z={z} y={y} body={b} lid={l}")

# also rear vents region
for z in (54.0, 55.0, 56.0):
    print(f"z={z} body +Y faces:", hits("Enclosure_Body", (0, 80, z), (0, -1, 0)))
