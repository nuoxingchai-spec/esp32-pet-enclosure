import bpy, bmesh
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
for name in ('Enclosure_Body', 'Enclosure_Lid'):
    o = bpy.data.objects[name]
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(o.data); bm.free()
    o.data.update()
    zero = sum(1 for p in o.data.polygons if p.area < 1e-10)
    smooth = sum(1 for p in o.data.polygons if p.use_smooth)
    print(f"APPLIED {name} v={len(o.data.vertices)} f={len(o.data.polygons)} zero={zero} smooth_polys={smooth}")
bpy.ops.wm.save_mainfile(filepath=BLEND)
print('SAVED')
