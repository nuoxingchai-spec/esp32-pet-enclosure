import bpy, bmesh
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
WORK  = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev13_smooth.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)

old_btn = bpy.data.meshes['Button_Top']
lid = bpy.data.objects['Enclosure_Lid']
old_lid = lid.data
print('OLD', old_btn.name, len(old_btn.vertices), '|', old_lid.name, len(old_lid.vertices))

with bpy.data.libraries.load(WORK, link=False) as (src, dst):
    dst.meshes = ['Button_Top', 'Enclosure_Lid.007']
new_btn, new_lid = dst.meshes
assert new_btn and new_lid, 'load failed'
print('LOADED', new_btn.name, len(new_btn.vertices), len(new_btn.polygons),
      '|', new_lid.name, len(new_lid.vertices), len(new_lid.polygons))

btn_objs = [o for o in bpy.data.objects if o.type == 'MESH' and o.data == old_btn]
print('BUTTON OBJECTS', sorted(o.name for o in btn_objs))
btn_name = old_btn.name
for o in btn_objs:
    o.data = new_btn
lid_name = old_lid.name
lid.data = new_lid
if old_btn.users == 0:
    bpy.data.meshes.remove(old_btn)
if old_lid.users == 0:
    bpy.data.meshes.remove(old_lid)
new_btn.name = btn_name
new_lid.name = lid_name
print('RENAMED', new_btn.name, new_lid.name)

def audit(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    nm = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    bnd = sum(1 for e in bm.edges if len(e.link_faces) < 2)
    zero = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    vol = bm.calc_volume(signed=True); bm.free()
    print(f"PROMOTED {o.name:16s} v={len(o.data.vertices):5d} f={len(o.data.polygons):5d} nm={nm} bnd={bnd} zero={zero} vol={vol:.2f} dims={o.dimensions.x:.2f}x{o.dimensions.y:.2f}x{o.dimensions.z:.2f}")

for o in btn_objs + [lid]:
    audit(o)

print('SCENE objects', len(bpy.context.scene.objects), 'camera', bpy.context.scene.camera.name if bpy.context.scene.camera else None)
bpy.ops.wm.save_mainfile(filepath=BLEND)
print('SAVED', BLEND)
