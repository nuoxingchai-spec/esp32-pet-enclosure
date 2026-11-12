import bpy, bmesh
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
body=bpy.data.objects['Enclosure_Body']
def report(tag):
    bm=bmesh.new(); bm.from_mesh(body.data)
    nm=sum(1 for e in bm.edges if len(e.link_faces)!=2); bnd=sum(1 for e in bm.edges if len(e.link_faces)<2)
    z9=sum(1 for f in bm.faces if f.calc_area()<1e-9); z10=sum(1 for f in bm.faces if f.calc_area()<1e-10)
    print(f"{tag} v={len(bm.verts)} f={len(bm.faces)} nm={nm} bnd={bnd} zero1e-9={z9} zero1e-10={z10} vol={bm.calc_volume(signed=True):.1f}")
    bm.free()
report('BEFORE')
bm=bmesh.new(); bm.from_mesh(body.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-3)
bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(body.data); bm.free(); body.data.update(); bpy.context.view_layer.update()
report('AFTER')
bpy.ops.wm.save_mainfile(filepath=BLEND)
print('SAVED')
