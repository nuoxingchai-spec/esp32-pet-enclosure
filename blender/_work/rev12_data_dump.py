import bpy
print("BLENDFILE", bpy.data.filepath)
print("SCENES", [s.name for s in bpy.data.scenes])
print("OBJECTS", len(bpy.data.objects))
for o in sorted(bpy.data.objects, key=lambda x: x.name):
    me = o.data
    vf = f"v={len(me.vertices)} f={len(me.polygons)}" if o.type == "MESH" else ""
    mods = ",".join(m.type for m in o.modifiers)
    print(f"OB {o.name:<26} {o.type:<7} hid={o.hide_get()} hr={o.hide_render} parent={o.parent.name if o.parent else '-'} {vf} mods=[{mods}]")
print("MESHES", len(bpy.data.meshes))
print("COLLS", len(bpy.data.collections), sorted(c.name for c in bpy.data.collections))
for c in bpy.data.collections:
    print("COLLDATA", c.name, "objs=", [o.name for o in c.objects])
print("CAMERAS", [o.name for o in bpy.data.objects if o.type == "CAMERA"])
print("LIGHTS", [(o.name, o.data.type) for o in bpy.data.objects if o.type == "LIGHT"])
print("WORLD", [(w.name, tuple(round(c, 3) for c in w.color)) for w in bpy.data.worlds])
print("MATS", [m.name for m in bpy.data.materials])
for s in bpy.data.scenes:
    print("SCENE", s.name, "camera=", s.camera.name if s.camera else "-", "engine=", s.render.engine, "res=", s.render.resolution_x, s.render.resolution_y, "collections=", [c.name for c in s.collection.children_recursive])
