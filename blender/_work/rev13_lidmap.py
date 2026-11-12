import bpy, math, os
from mathutils import Vector

ROOT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5"
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, r"blender\robot_dog_enclosure_v3.blend"))
sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()

lid = bpy.data.objects['Enclosure_Lid']
print("LID users:", lid.data.users, "mesh:", lid.data.name, "mods:", [m.type for m in lid.modifiers])
print("LID parent:", lid.parent, "colls:", [c.name for c in lid.users_collection])
print("LID mw:", [round(v,4) for r in lid.matrix_world for v in r])
print("LID local bbox z:", min(v[2] for v in lid.bound_box), max(v[2] for v in lid.bound_box))
print("LID hide:", lid.hide_viewport, lid.hide_render, lid.hide_get())

btn = bpy.data.objects['Button_Top_1']
print("BTN mesh users:", btn.data.users, "shade smooth faces:",
      sum(1 for p in btn.data.polygons if p.use_smooth), "/", len(btn.data.polygons))
print("BTN mods:", [m.type for m in btn.modifiers], "parent:", btn.parent,
      "colls:", [c.name for c in btn.users_collection])

CENTERS = [(-24.83, -35.47), (-24.83, -42.45), (-24.83, -49.47)]
print("--- lid top map (local z) around each button; lid local = world z-14 ---")
for (cx, cy) in CENTERS:
    print(f"center {cx},{cy}")
    for dy in (-8, -6, -4, -3, -2, -1, 0, 1, 2, 3, 4, 6, 8):
        row = []
        for dx in (-8, -6, -4, -3, -2.5, -2.2, -2.1, -2.0, 0, 2.0, 2.1, 2.2, 2.5, 3, 4, 6, 8):
            org = Vector((cx + dx, cy + dy, 58.0))
            ok, loc, nor, idx = lid.ray_cast(org, Vector((0, 0, -1)), distance=10.0, depsgraph=dg)
            row.append('---' if not ok else f"{loc.z:4.1f}")
        print(f"  dy={dy:4.0f}: " + ' '.join(row))

print("--- lid underside near buttons (local z, cast up) ---")
for (cx, cy) in CENTERS:
    for dx, dy in ((0,0), (2.5,0), (0,2.5), (4,0), (6,0)):
        org = Vector((cx + dx, cy + dy, 40.0))
        ok, loc, nor, idx = lid.ray_cast(org, Vector((0, 0, 1)), distance=20.0, depsgraph=dg)
        print(f"  dx={dx:4.1f} dy={dy:4.1f} -> " + ('MISS' if not ok else f"z={loc.z:.3f} n={tuple(round(x,2) for x in nor)}"))
print("DONE")
