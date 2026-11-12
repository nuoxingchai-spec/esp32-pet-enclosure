import bpy, sys
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
WRITE = "--write" in argv
BASE = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\robot_dog_enclosure_v3_prev_2026-11-11.blend"
SRC = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev11_final.blend"
DST = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"

def snap_scene():
    sc = bpy.context.scene
    return {
        "camera": sc.camera.name if sc.camera else None,
        "engine": sc.render.engine,
        "res": (sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage),
        "film_transparent": sc.render.film_transparent,
        "view": (sc.view_settings.view_transform, sc.view_settings.look,
                 round(sc.view_settings.exposure, 4), round(sc.view_settings.gamma, 4)),
        "display": sc.display_settings.display_device,
        "world": (sc.world.name if sc.world else None,
                  tuple(round(c, 4) for c in sc.world.color) if sc.world else None,
                  sc.world.use_nodes if sc.world else None),
    }

def snap_objects():
    d = {}
    for o in bpy.data.objects:
        d[o.name] = {
            "hide": o.hide_get(), "hr": o.hide_render, "hv": o.hide_viewport,
            "color": tuple(round(c, 4) for c in o.color),
            "display_type": o.display_type, "show_in_front": o.show_in_front,
            "visible_camera": o.visible_camera, "visible_shadow": o.visible_shadow,
            "visible_diffuse": o.visible_diffuse,
            "mw": tuple(round(x, 6) for row in o.matrix_world for x in row),
        }
    return d

bpy.ops.wm.open_mainfile(filepath=BASE)
base_scene = snap_scene()
base_objs = snap_objects()

bpy.ops.wm.open_mainfile(filepath=SRC)
src_scene = snap_scene()
src_objs = snap_objects()

print("SCENE-BASE", base_scene)
print("SCENE-SRC ", src_scene)
for k in base_scene:
    if base_scene[k] != src_scene[k]:
        print("SCENE-DIFF", k, base_scene[k], "->", src_scene[k])

print("EXTRA-OBJECTS", sorted(set(src_objs) - set(base_objs)))
print("MISSING-OBJECTS", sorted(set(base_objs) - set(src_objs)))
for name in sorted(set(base_objs) & set(src_objs)):
    diffs = {k: (base_objs[name][k], src_objs[name][k])
             for k in base_objs[name] if base_objs[name][k] != src_objs[name][k]}
    if diffs:
        print("OBJ-DIFF", name, diffs)

if WRITE:
    for name in ("Shoulder_Cutter", "Seam_Cutter"):
        ob = bpy.data.objects.get(name)
        if ob:
            me = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)
    for name, attrs in base_objs.items():
        ob = bpy.data.objects.get(name)
        if not ob:
            continue
        hidden_vp = attrs["hide"]
        ob.hide_viewport = attrs["hv"]
        ob.hide_set(hidden_vp)
        ob.hide_render = attrs["hr"]
        ob.color = attrs["color"]
        ob.display_type = attrs["display_type"]
        ob.show_in_front = attrs["show_in_front"]
        ob.visible_camera = attrs["visible_camera"]
        ob.visible_shadow = attrs["visible_shadow"]
        ob.visible_diffuse = attrs["visible_diffuse"]
    bpy.context.view_layer.update()
    bad = []
    for name, attrs in base_objs.items():
        ob = bpy.data.objects.get(name)
        if not ob:
            continue
        mw = tuple(round(x, 5) for row in ob.matrix_world for x in row)
        if mw != attrs["mw"]:
            bad.append((name, attrs["mw"], mw))
    print("MATRIX-MISMATCH", len(bad))
    for name, want, got in bad:
        print("  MW", name, want, got)
    sc = bpy.context.scene
    sc.camera = bpy.data.objects[base_scene["camera"]]
    sc.render.engine = base_scene["engine"]
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = base_scene["res"]
    sc.render.film_transparent = base_scene["film_transparent"]
    sc.view_settings.view_transform, sc.view_settings.look = base_scene["view"][0], base_scene["view"][1]
    sc.view_settings.exposure, sc.view_settings.gamma = base_scene["view"][2], base_scene["view"][3]
    sc.display_settings.display_device = base_scene["display"]
    w = bpy.data.worlds.get(base_scene["world"][0])
    if w:
        sc.world = w
        w.color = base_scene["world"][1]
        w.use_nodes = base_scene["world"][2]
    print("FINAL-OBJECTS", len(bpy.data.objects))
    print("FINAL-SCENE", snap_scene())
    bpy.ops.wm.save_as_mainfile(filepath=DST)
    print("SAVED", DST, "bytes", __import__("os").path.getsize(DST))
