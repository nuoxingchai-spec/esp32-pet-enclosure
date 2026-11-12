import bpy, bmesh
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
body = bpy.data.objects['Enclosure_Body']
# box cutter: remove two inner ribs on -X rear that collide with lid lip
cm = bpy.data.meshes.new('cutm'); bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1)
bmesh.ops.scale(bm, vec=(1.30, 18.0, 0.80), verts=bm.verts)  # 1.30 x 18.0 x 0.80
center = (-36.00, -42.5, 59.05)  # x -36.65..-35.35, y -51.5..-33.5, z 58.65..59.45
bmesh.ops.translate(bm, vec=center, verts=bm.verts)
bm.to_mesh(cm); bm.free()
co = bpy.data.objects.new('cutobj', cm); bpy.context.scene.collection.objects.link(co)
bpy.context.view_layer.objects.active = body
m = body.modifiers.new('b','BOOLEAN'); m.operation='DIFFERENCE'; m.solver='EXACT'; m.object=co
bpy.ops.object.modifier_apply(modifier=m.name)
bpy.data.objects.remove(co, do_unlink=True)
bm = bmesh.new(); bm.from_mesh(body.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
bm.to_mesh(body.data); bm.free(); body.data.update()
bm = bmesh.new(); bm.from_mesh(body.data)
print(f"BODY v={len(bm.verts)} f={len(bm.faces)} nm={sum(1 for e in bm.edges if len(e.link_faces)!=2)} "
      f"bnd={sum(1 for e in bm.edges if len(e.link_faces)<2)} zero={sum(1 for f in bm.faces if f.calc_area()<1e-9)} "
      f"vol={bm.calc_volume(signed=True):.2f}")
bm.free()
bpy.ops.wm.save_mainfile(filepath=BLEND)
print('SAVED')
