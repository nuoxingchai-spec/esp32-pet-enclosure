import bpy, bmesh
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage3.blend')
body=bpy.data.objects['Enclosure_Body']
def box(name,x0,x1,y0,y1,z0,z1):
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    vs=[bm.verts.new((x0,y0,z0)),bm.verts.new((x1,y0,z0)),bm.verts.new((x1,y1,z0)),bm.verts.new((x0,y1,z0))]
    f=bm.faces.new(vs); ret=bmesh.ops.extrude_face_region(bm,geom=[f])
    ext=[e for e in ret['geom'] if isinstance(e,bmesh.types.BMVert)]
    bmesh.ops.translate(bm,vec=(0,0,z1-z0),verts=ext); bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(me); bm.free(); o=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(o); return o
def inter(a,b,label):
    d=a.copy(); d.data=a.data.copy(); bpy.context.scene.collection.objects.link(d)
    md=d.modifiers.new('b','BOOLEAN'); md.operation='INTERSECT'; md.solver='EXACT'; md.object=b
    bpy.context.view_layer.objects.active=d; d.select_set(True); bpy.ops.object.modifier_apply(modifier=md.name)
    bm=bmesh.new(); bm.from_mesh(d.data); v=abs(bm.calc_volume())
    if bm.verts:
        xs=[v0.co.x for v0 in bm.verts]; ys=[v0.co.y for v0 in bm.verts]; zs=[v0.co.z for v0 in bm.verts]
        bb=f' x[{min(xs):.2f},{max(xs):.2f}] y[{min(ys):.2f},{max(ys):.2f}] z[{min(zs):.2f},{max(zs):.2f}]'
    else: bb=' empty'
    bm.free(); bpy.data.objects.remove(d,do_unlink=True)
    print(label, round(v,4), bb)
for z0,z1,tag in ((55.4,58.0,'A'),(55.5,58.1,'B'),(55.6,58.2,'C')):
    c=box('usb',-21.4,-13.0,-70,-56.5,z0,z1)
    inter(body,c,f'USB z[{z0},{z1}]')
    bpy.data.objects.remove(c,do_unlink=True)
# shell against the outer wall only, 3 mm in
c=box('usb',-21.4,-13.0,-70,-60.5,55.5,58.1)
inter(body,c,'USB 3.5mm-in')
bpy.data.objects.remove(c,do_unlink=True)
print('DONE2')
