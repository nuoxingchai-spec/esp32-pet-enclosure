import bpy
bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev6_corner.blend")
for o in bpy.data.objects:
    mods = [(m.name, m.type) for m in o.modifiers] if o.type == 'MESH' else []
    if o.type == 'MESH' or o.type == 'EMPTY':
        print(o.name, o.type, "hide_viewport", o.hide_viewport, "hide_render", o.hide_render, "mods", mods, "loc", tuple(round(c, 2) for c in o.location), "dim", tuple(round(c, 2) for c in o.dimensions))
print("collections", [c.name for c in bpy.data.collections])
