import bpy, bmesh
from mathutils import Vector
F = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob = bpy.data.objects['Enclosure_Body']; mw = ob.matrix_world
bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(mw)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()

hub = None
for v in bm.verts:
    if abs(v.co.z-54.35)<0.01 and abs(v.co.x-39.014)<0.05 and abs(v.co.y+60.395)<0.05:
        hub = v; break
print('HUB', hub.index if hub else None, tuple(round(q,3) for q in hub.co) if hub else '')
if hub:
    for f in hub.link_faces:
        vs=[tuple(round(q,2) for q in v.co) for v in f.verts]
        print(f"  face n=({f.normal.x:5.2f},{f.normal.y:5.2f},{f.normal.z:5.2f}) A={f.calc_area():8.3f} verts={vs}")

print("\nverts x>38.9, z 50..54.36, y -61..-20:")
rows=[]
for v in bm.verts:
    if v.co.x>38.9 and 50.0 < v.co.z < 54.36 and -61.0 < v.co.y < -20.0:
        rows.append((round(v.co.z,3), round(v.co.y,3), round(v.co.x,3), v.index))
for r in sorted(rows, key=lambda t:(-t[0], -t[1])):
    print(' v', r)

print("\nverts z 53.9..54.36, any x, y -61..-20, outer (x>30):")
rows=[]
for v in bm.verts:
    if 53.9 < v.co.z < 54.36 and -61.0 < v.co.y < -20.0 and v.co.x>30.0:
        rows.append((round(v.co.x,2), round(v.co.y,2), round(v.co.z,3)))
for r in sorted(rows, key=lambda t:(-t[1])):
    print(' v', r)
bm.free()
print('DONE')
