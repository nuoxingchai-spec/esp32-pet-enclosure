import bpy, sys
argv = sys.argv[sys.argv.index("--") + 1:]
print("BLENDFILE", argv[0])

def walk(coll, depth=0):
    print("  " * depth + "COLL", coll.name, "hide_vp=", coll.hide_viewport, "hide_render=", coll.hide_render)
    for ob in coll.objects:
        me = ob.data
        vf = f"v={len(me.vertices)} f={len(me.polygons)}" if ob.type == "MESH" else ""
        mods = ",".join(m.type for m in ob.modifiers)
        print("  " * (depth + 1) + f"OB {ob.name:<28} {ob.type:<8} hid={ob.hide_get()} hr={ob.hide_render} "
              f"parent={ob.parent.name if ob.parent else '-'} {vf} mods=[{mods}] "
              f"loc=({ob.location.x:.3f},{ob.location.y:.3f},{ob.location.z:.3f})")
    for ch in coll.children:
        walk(ch, depth + 1)

for sc in bpy.data.scenes:
    print("SCENE", sc.name, "camera=", sc.camera.name if sc.camera else "-",
          "engine=", sc.render.engine, "res=", sc.render.resolution_x, sc.render.resolution_y)
    walk(sc.collection)
print("WORLD", [(w.name, tuple(round(c, 3) for c in w.color)) for w in bpy.data.worlds])
print("CAMERAS", [o.name for o in bpy.data.objects if o.type == "CAMERA"])
print("LIGHTS", [(o.name, o.type, o.data.type if o.data else "") for o in bpy.data.objects if o.type == "LIGHT"])
print("MATS", [m.name for m in bpy.data.materials])
