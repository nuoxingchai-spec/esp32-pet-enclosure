import bpy, bmesh
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath=r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage3.blend')
body = bpy.data.objects['Enclosure_Body']

def make_card(name, x0, x1, y0, y1, z0, z1):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vs = [bm.verts.new((x0, y0, z0)), bm.verts.new((x1, y0, z0)),
          bm.verts.new((x1, y1, z0)), bm.verts.new((x0, y1, z0))]
    f = bm.faces.new(vs)
    ret = bmesh.ops.extrude_face_region(bm, geom=[f])
    ext = [e for e in ret['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, z1 - z0), verts=ext)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    return o

def inter(a, b):
    d = a.copy()
    d.data = a.data.copy()
    bpy.context.scene.collection.objects.link(d)
    md = d.modifiers.new('b', 'BOOLEAN')
    md.operation = 'INTERSECT'
    md.solver = 'EXACT'
    md.object = b
    bpy.context.view_layer.objects.active = d
    d.select_set(True)
    bpy.ops.object.modifier_apply(modifier=md.name)
    bm = bmesh.new()
    bm.from_mesh(d.data)
    v = abs(bm.calc_volume())
    bm.free()
    bpy.data.objects.remove(d, do_unlink=True)
    return v

for x0, x1 in ((24, 39), (30, 45), (34, 49)):
    for zc in (56.4, 57.25, 58.1):
        c = make_card('c', x0, x1, -38.0, -27.0, zc - 0.5, zc + 0.5)
        v = inter(body, c)
        print(f'card x[{x0},{x1}] zc {zc:.2f}: overlap {v:.4f} mm3')
        bpy.data.objects.remove(c, do_unlink=True)

# identical card as rendered (half inserted)
c = make_card('c', 34, 49, -38, -27, 56.75, 57.75)
print('render card overlap', round(inter(body, c), 4))
bpy.data.objects.remove(c, do_unlink=True)
print('SD TEST DONE')
