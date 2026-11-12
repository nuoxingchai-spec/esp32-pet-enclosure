import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage5b.blend")
scene = bpy.context.scene

def dup(n):
    o = bpy.data.objects[n]; d = o.copy(); d.data = o.data.copy(); scene.collection.objects.link(d)
    d.hide_render = False
    for m in list(d.modifiers): d.modifiers.remove(m)
    return d

def cut(d, center, size):
    cm = bpy.data.meshes.new('c'); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bmesh.ops.translate(bm, vec=center, verts=bm.verts)
    bm.to_mesh(cm); bm.free()
    co = bpy.data.objects.new('c', cm); scene.collection.objects.link(co)
    bpy.context.view_layer.objects.active = d
    md = d.modifiers.new('b', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.solver = 'EXACT'; md.object = co
    bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(co, do_unlink=True)

names = ['Enclosure_Lid', 'PCB_Board', 'PCB_Components', 'Button_Top_2']
copies = []
for n in names:
    d = dup(n)
    cut(d, (-24.5-150, -42.45, 62.0), (300, 120, 80))
    cut(d, (-8+150, -42.45, 62.0), (300, 120, 80))
    copies.append(d)

bpy.context.view_layer.update()
for d in copies:
    bb = [d.matrix_world @ Vector(c) for c in d.bound_box]
    print('SEC', d.name, 'x', round(min(p.x for p in bb),2), round(max(p.x for p in bb),2),
          'y', round(min(p.y for p in bb),2), round(max(p.y for p in bb),2),
          'z', round(min(p.z for p in bb),2), round(max(p.z for p in bb),2))

# raycast from the section camera
trees = []
for d in copies:
    bm = bmesh.new(); bm.from_mesh(d.data); bm.transform(d.matrix_world)
    trees.append((d.name, BVHTree.FromBMesh(bm))); bm.free()
for z in (60.0, 62.0, 64.0, 66.0, 67.4, 68.2):
    hit = None
    for name, t in trees:
        loc, nor, idx, dist = t.ray_cast(Vector((-130, -42.45, z)), Vector((1,0,0)), 400)
        if loc is not None and (hit is None or dist < hit[2]):
            hit = (name, loc, dist)
    print('RAY z', z, '->', hit[0] if hit else None,
          tuple(round(v,2) for v in hit[1]) if hit else '')
print('DONE')
