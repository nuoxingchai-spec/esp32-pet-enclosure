import bpy, bmesh
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
for name in ('Enclosure_Body',):
    o = bpy.data.objects[name]
    me = o.data.copy()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
    zero = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
    tiny = sum(1 for f in bm.faces if f.calc_area() < 1e-6)
    nm = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    bnd = sum(1 for e in bm.edges if len(e.link_faces) < 2)
    v = len(bm.verts); f = len(bm.faces)
    bm.free(); bpy.data.meshes.remove(me)
    print(f"TRI {name} v={v} f={f} zero={zero} tiny={tiny} nm={nm} bnd={bnd}")
