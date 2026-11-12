import bpy
BASE = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\robot_dog_enclosure_v3_prev_2026-11-11.blend"
DST = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"

def snap():
    d = {}
    for o in bpy.data.objects:
        d[o.name] = {
            "hide": o.hide_get(), "hr": o.hide_render, "hv": o.hide_viewport,
            "color": tuple(round(c, 4) for c in o.color),
            "display_type": o.display_type, "show_in_front": o.show_in_front,
            "visible_camera": o.visible_camera, "visible_shadow": o.visible_shadow,
            "visible_diffuse": o.visible_diffuse,
            "mw": [o.matrix_world[i][j] for i in range(4) for j in range(4)],
        }
    return d

bpy.ops.wm.open_mainfile(filepath=BASE)
base = snap()
bpy.ops.wm.open_mainfile(filepath=DST)
dst = snap()

print("OBJECTS", len(dst), "EXTRA", sorted(set(dst) - set(base)), "MISSING", sorted(set(base) - set(dst)))
bad = 0
for n in sorted(set(base) & set(dst)):
    for k in ("hide", "hr", "hv", "color", "display_type", "show_in_front",
              "visible_camera", "visible_shadow", "visible_diffuse"):
        if base[n][k] != dst[n][k]:
            print("DIFF", n, k, base[n][k], "->", dst[n][k]); bad += 1
    if any(abs(a - b) > 1e-3 for a, b in zip(base[n]["mw"], dst[n]["mw"])):
        print("MWDIFF", n, [round(b - a, 4) for a, b in zip(base[n]["mw"], dst[n]["mw"])]); bad += 1
print("ATTR-MATRIX-DIFFS", bad)

for n in ("Enclosure_Body", "Enclosure_Lid", "LED_Diffuser_Ring", "Belly_Pan",
          "Button_Top_1", "Ear_R", "Tail", "PCB_Board", "Touch_Module_Fit",
          "SG90_Fit_1", "OLED_1p3_Module", "Speaker_3070", "Battery_103450"):
    o = bpy.data.objects[n]
    t = o.matrix_world.translation
    print(f"MW {n:20s} loc_z={o.location.z:8.3f} world_z={t.z:8.3f} x={t.x:7.3f} y={t.y:7.3f} hv={o.hide_viewport} hr={o.hide_render}")
print('DONE')
