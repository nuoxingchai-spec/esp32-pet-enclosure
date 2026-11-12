import bpy
bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev6_corner.blend")
ob = bpy.data.objects["Enclosure_Body"]
me = ob.data
for Y in (40.0, 45.0, -40.0, -45.0):
    print("=== section y=%.1f ===" % Y)
    segs = []
    for e in me.edges:
        a = me.vertices[e.vertices[0]].co; b = me.vertices[e.vertices[1]].co
        if (a.y - Y) * (b.y - Y) > 0: continue
        if abs(a.y - b.y) < 1e-9: continue
        t = (Y - a.y) / (b.y - a.y)
        p = a.lerp(b, t)
        if not (37.5 < abs(p.x) < 40.5 and 38.0 < p.z < 42.0): continue
        segs.append((round(p.x, 4), round(p.z, 4), round((a.x + b.x) / 2, 2)))
    seen = set(); out = []
    for s in sorted(segs):
        if s in seen: continue
        seen.add(s); out.append(s)
    for s in out: print("   x=%.4f z=%.4f" % (s[0], s[1]))
