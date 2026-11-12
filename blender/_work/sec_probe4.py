import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage5b.blend")
scene = bpy.context.scene

def fbvh(d):
    bm = bmesh.new(); bm.from_mesh(d.data); bm.transform(d.matrix_world)
    t = BVHTree.FromBMesh(bm); bm.free(); return t

def cut_test(solver, center, size, label):
    o = bpy.data.objects['Enclosure_Lid']
    d = o.copy(); d.data = o.data.copy(); scene.collection.objects.link(d)
    cm = bpy.data.meshes.new('c'); bm = bmesh.new(); bmesh.ops.create_cube(bm,size=1)
    bmesh.ops.scale(bm,vec=size,verts=bm.verts); bmesh.ops.translate(bm,vec=center,verts=bm.verts)
    bm.to_mesh(cm); bm.free()
    co = bpy.data.objects.new('c',cm); scene.collection.objects.link(co)
    bpy.context.view_layer.objects.active = d
    m = d.modifiers.new('b','BOOLEAN'); m.operation='DIFFERENCE'; m.solver=solver; m.object=co
    try:
        bpy.ops.object.modifier_apply(modifier=m.name)
    except Exception as e:
        print('APPLY FAIL', label, e)
    bpy.data.objects.remove(co, do_unlink=True)
    t = fbvh(d)
    loc,_,_,_ = t.ray_cast(Vector((-130,-42.45,60)), Vector((1,0,0)), 400)
    print('TEST', label, 'verts', len(d.data.vertices), 'ray', tuple(round(v,2) for v in loc) if loc else None)
    bpy.data.objects.remove(d, do_unlink=True)

cut_test('FLOAT', (-174.83,-42.45,62), (300,120,80), 'FLOAT huge')
cut_test('MANIFOLD', (-42.4,-42.45,62), (35.2,30,25), 'MANIFOLD local')

# direct bisect on a copy
o = bpy.data.objects['Enclosure_Lid']
d = o.copy(); d.data = o.data.copy(); scene.collection.objects.link(d)
bm = bmesh.new(); bm.from_mesh(d.data)
# local plane x = -24.83 (object x == world x)
res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(-24.83,0,0), plane_no=(1,0,0), clear_inner=True, clear_outer=False)
print('BISECT result geom', len(res['geom_cut']), 'verts', len(bm.verts), 'faces', len(bm.faces))
bm.to_mesh(d.data); bm.free()
t = fbvh(d)
loc,_,_,_ = t.ray_cast(Vector((-130,-42.45,60)), Vector((1,0,0)), 400)
print('BISECT ray', tuple(round(v,2) for v in loc) if loc else None)
print('DONE')
