import bpy, bmesh
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
o=bpy.data.objects['Tail']
me=o.data
bm=bmesh.new(); bm.from_mesh(me)
areas=sorted(f.calc_area() for f in bm.faces)
print("min areas", areas[:6])
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-3)
bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
print("after v",len(bm.verts),"f",len(bm.faces),"zero",sum(1 for f in bm.faces if f.calc_area()<1e-9),"nm",sum(1 for e in bm.edges if len(e.link_faces)!=2),"bnd",sum(1 for e in bm.edges if len(e.link_faces)<2),"vol",bm.calc_volume(signed=True))
bm.to_mesh(me); bm.free(); me.update()
bpy.ops.wm.save_mainfile(filepath=BLEND)
print('SAVED')
