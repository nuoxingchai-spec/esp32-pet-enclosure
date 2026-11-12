import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage5b.blend")
scene = bpy.context.scene

def test(center, size, label):
    o = bpy.data.objects['Enclosure_Lid']
    d = o.copy(); d.data = o.data.copy(); scene.collection.objects.link(d)
    cm = bpy.data.meshes.new('c'); bm = bmesh.new(); bmesh.ops.create_cube(bm,size=1)
    bmesh.ops.scale(bm,vec=size,verts=bm.verts); bmesh.ops.translate(bm,vec=center,verts=bm.verts)
    bm.to_mesh(cm); bm.free()
    co = bpy.data.objects.new('c',cm); scene.collection.objects.link(co)
    bpy.context.view_layer.objects.active = d
    m = d.modifiers.new('b','BOOLEAN'); m.operation='DIFFERENCE'; m.solver='EXACT'; m.object=co
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(co, do_unlink=True)
    bm = bmesh.new(); bm.from_mesh(d.data); bm.transform(d.matrix_world)
    t = BVHTree.FromBMesh(bm)
    hits = []
    for yy in (-42.45, -10.0, 30.0):
        loc, nor, idx, dist = t.ray_cast(Vector((-130, yy, 60)), Vector((1,0,0)), 400)
        hits.append((yy, tuple(round(v,2) for v in loc) if loc else None))
    print('TEST', label, 'verts', len(d.data.vertices), 'hit', hits)
    bm.free()
    bpy.data.objects.remove(d, do_unlink=True)

test((-30,-42.45,63), (10,10,10), 'small cube')
test((-42.4,-42.45,62), (35.2,30,25), 'local near box')
test((-174.83,-42.45,62), (300,120,80), 'huge near box')
test((-42.4,-42.45,62), (35.2,200,25), 'medium y200')
print('DONE')
