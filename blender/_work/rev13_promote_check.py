import bpy, sys, os

def dump(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    sc = bpy.context.scene
    rows = []
    for o in sc.objects:
        me = o.data if o.type == 'MESH' else None
        rows.append((o.name, o.type, tuple(round(v,3) for v in o.location),
                     len(me.vertices) if me else 0, len(me.polygons) if me else 0,
                     o.hide_viewport, o.hide_render))
    return sc.name, sc.camera.name if sc.camera else None, sorted(rows)

a = dump(r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend")
b = dump(r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev13_smooth.blend")
print("DELIV sc:", a[0], "cam:", a[1], "objects:", len(a[2]))
print("WORK  sc:", b[0], "cam:", b[1], "objects:", len(b[2]))
na = {r[0] for r in a[2]}; nb = {r[0] for r in b[2]}
print("only_in_deliverable:", sorted(na - nb))
print("only_in_work:", sorted(nb - na))
da = {r[0]: r for r in a[2]}; db = {r[0]: r for r in b[2]}
for n in sorted(na & nb):
    if da[n][3:] != db[n][3:]:
        print("DIFF", n, "deliv", da[n][3:], "work", db[n][3:])
