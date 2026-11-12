import bpy, bmesh, math
from mathutils import Vector

P = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=P)
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world; mi = mw.inverted(); M3i = mw.to_3x3().inverted()
dg = bpy.context.evaluated_depsgraph_get()
print("MW", [round(v, 3) for v in mw.translation])

def rx(y, z):
    org = mi @ Vector((60.0, y, z)); d = (M3i @ Vector((-1, 0, 0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=200.0, depsgraph=dg)
    if not ok: return None
    return round((mw @ loc).x, 4)
print("clean +X profile")
zs = [52.5 + 0.05 * i for i in range(61)]
print("z    " + " ".join(f"{z:6.2f}" for z in zs[::2]))
for y in (-20.0, -30.0, -45.0, -50.0, 0.0, 30.0):
    row = [rx(y, z) for z in zs]
    print(f"y{y:6.1f} " + " ".join(f"{v:6.3f}" if v else "  --  " for v in row[::2]))
    # step detection
    jump = []
    for i in range(1, len(row)):
        if row[i] is not None and row[i-1] is not None and abs(row[i]-row[i-1]) > 0.004:
            jump.append((round(zs[i],2), round(row[i-1],4), round(row[i],4)))
    print("   jumps(>4um/step):", jump)

def ry(x, z, sy=-1):
    org = mi @ Vector((x, sy * 80.0, z)); d = (M3i @ Vector((0, -sy, 0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=200.0, depsgraph=dg)
    if not ok: return None
    return round(abs((mw @ loc).y), 4)
print("clean -Y front profile")
for x in (0.0, 15.0, -25.0):
    row = [ry(x, z) for z in zs]
    print(f"x{x:6.1f} " + " ".join(f"{v:6.3f}" if v else "  --  " for v in row[::2]))
    jump = []
    for i in range(1, len(row)):
        if row[i] is not None and row[i-1] is not None and abs(row[i]-row[i-1]) > 0.004:
            jump.append((round(zs[i],2), round(row[i-1],4), round(row[i],4)))
    print("   jumps:", jump)

bm = bmesh.new(); bm.from_mesh(body.data)
print("--- faces near +X seam, y=-50 area ---")
for f in bm.faces:
    c = f.calc_center_median()
    if c.x > 37.0 and abs(c.y + 50.0) < 3.0 and 39.3 < c.z < 41.3:
        vs = " ".join("(%.2f,%.2f,%.3f)" % (v.co.x, v.co.y, v.co.z) for v in f.verts)
        print("  c=(%.3f,%.3f,%.3f) n=(%.2f,%.2f,%.2f) a=%.5f  %s" % (c.x, c.y, c.z, f.normal.x, f.normal.y, f.normal.z, f.calc_area(), vs))
bm.free()
