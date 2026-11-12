import bpy, bmesh
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage3.blend')
body=bpy.data.objects['Enclosure_Body']
def box(name,x0,x1,y0,y1,z0,z1):
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    vs=[bm.verts.new((x0,y0,z0)),bm.verts.new((x1,y0,z0)),bm.verts.new((x1,y1,z0)),bm.verts.new((x0,y1,z0))]
    f=bm.faces.new(vs); ret=bmesh.ops.extrude_face_region(bm,geom=[f])
    ext=[e for e in ret['geom'] if isinstance(e,bmesh.types.BMVert)]
    bmesh.ops.translate(bm,vec=(0,0,z1-z0),verts=ext); bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(me); bm.free(); o=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(o); return o
def inter(a,b):
    d=a.copy(); d.data=a.data.copy(); bpy.context.scene.collection.objects.link(d)
    md=d.modifiers.new('b','BOOLEAN'); md.operation='INTERSECT'; md.solver='EXACT'; md.object=b
    bpy.context.view_layer.objects.active=d; d.select_set(True); bpy.ops.object.modifier_apply(modifier=md.name)
    bm=bmesh.new(); bm.from_mesh(d.data); v=abs(bm.calc_volume()); bm.free(); bpy.data.objects.remove(d,do_unlink=True); return v
# USB-C plug metal shell 8.4 x 2.6, inserted 13 mm
c=box('usb',-21.4,-13.0,-70,-56.5,55.2,57.8)
print('USB shell overlap', round(inter(body,c),4))
bpy.data.objects.remove(c,do_unlink=True)
# USB shell only just through wall, 6 mm inside
c=box('usb2',-21.4,-13.0,-70,-58.0,55.2,57.8)
print('USB shell 6mm overlap', round(inter(body,c),4))
bpy.data.objects.remove(c,do_unlink=True)
# narrower shell 4.0 wide at left side
c=box('usb3',-22.4,-18.4,-70,-56.5,55.4,58.6)
print('USB narrow-left overlap', round(inter(body,c),4))
bpy.data.objects.remove(c,do_unlink=True)
# switch toggle 4 x 2, 8 mm in
c=box('sw',16.2,20.2,-70,-56.0,56.2,58.2)
print('Switch overlap', round(inter(body,c),4))
bpy.data.objects.remove(c,do_unlink=True)
print('PORT TEST DONE')
