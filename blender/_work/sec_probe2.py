import bpy
bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage5b.blend")
for n in ['Enclosure_Lid','Button_Top_2','PCB_Board']:
    o = bpy.data.objects[n]
    print(n, 'loc', tuple(round(v,3) for v in o.location), 'rot', tuple(round(v,3) for v in o.rotation_euler),
          'scale', tuple(round(v,3) for v in o.scale), 'dims', tuple(round(v,3) for v in o.dimensions))
    print('  mods', [(m.name, m.type) for m in o.modifiers], 'shapekeys', bool(o.data.shape_keys),
          'verts', len(o.data.vertices), 'polys', len(o.data.polygons), 'materials', [ms.material.name if ms.material else None for ms in o.material_slots])
    print('  matrix', [tuple(round(v,3) for v in row) for row in o.matrix_world])
# test boolean on a fresh copy with a simple cube cut
import bmesh
scene = bpy.context.scene
def test(name, center, size):
    o = bpy.data.objects[name]
    d = o.copy(); d.data = o.data.copy(); scene.collection.objects.link(d)
    cm = bpy.data.meshes.new('c'); bm = bmesh.new(); bmesh.ops.create_cube(bm,size=1)
    bmesh.ops.scale(bm,vec=size,verts=bm.verts); bmesh.ops.translate(bm,vec=center,verts=bm.verts)
    bm.to_mesh(cm); bm.free()
    co = bpy.data.objects.new('c',cm); scene.collection.objects.link(co)
    bpy.context.view_layer.objects.active = d
    m = d.modifiers.new('b','BOOLEAN'); m.operation='DIFFERENCE'; m.solver='EXACT'; m.object=co
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(co, do_unlink=True)
    bb = [d.matrix_world @ __import__('mathutils').Vector(c) for c in d.bound_box]
    print('TEST', name, 'x', round(min(p.x for p in bb),2), round(max(p.x for p in bb),2),
          'y', round(min(p.y for p in bb),2), round(max(p.y for p in bb),2),
          'z', round(min(p.z for p in bb),2), round(max(p.z for p in bb),2))
    bpy.data.objects.remove(d, do_unlink=True)
test('Enclosure_Lid', (-24.5-150,-42.45,62), (300,120,80))
test('Enclosure_Lid', (-150,-42.45,62), (300,120,80))  # full x<0 half-space
test('Button_Top_2', (-24.5-150,-42.45,62), (300,120,80))
print('DONE')
