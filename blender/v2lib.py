import bpy, bmesh, math
from mathutils import Matrix, Vector

def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
    p = parent or bpy.context.scene.collection
    if c.name not in [x.name for x in p.children]:
        p.children.link(c)
    return c

def link(obj, c):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    c.objects.link(obj)

def mat(name, color, metallic=0.0, rough=0.45, alpha=1.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if b:
        b.inputs['Base Color'].default_value = (*color, 1.0)
        b.inputs['Metallic'].default_value = metallic
        b.inputs['Roughness'].default_value = rough
        if 'Alpha' in b.inputs:
            b.inputs['Alpha'].default_value = alpha
    m.diffuse_color = (*color, alpha)
    return m

def _finish(name, bm, m, c):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    c.objects.link(o)
    if m:
        me.materials.append(m)
    return o

def rbox(name, cx, cy, w, d, z0, z1, r=0.0, m=None, c=None, seg=16):
    w = max(w, 0.1); d = max(d, 0.1)
    r = min(r, w / 2 - 0.01, d / 2 - 0.01)
    if r <= 0.01:
        pts = [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]
    else:
        pts = []
        for ccx, ccy, a0 in ((w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)):
            for i in range(seg):
                a = math.radians(a0 + 90.0 * i / seg)
                pts.append((ccx + r*math.cos(a), ccy + r*math.sin(a)))
    bm = bmesh.new()
    vs = [bm.verts.new((x+cx, y+cy, z0)) for x, y in pts]
    f = bm.faces.new(vs)
    ret = bmesh.ops.extrude_face_region(bm, geom=[f])
    ext = [e for e in ret['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0,0,z1-z0), verts=ext)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _finish(name, bm, m, c or bpy.context.scene.collection)

def rboxmm(name, x0, x1, y0, y1, z0, z1, r=0.0, m=None, c=None, seg=16):
    return rbox(name, (x0+x1)/2, (y0+y1)/2, x1-x0, y1-y0, z0, z1, r, m, c, seg)

def cylz(name, cx, cy, z0, z1, dia, m=None, c=None, seg=32):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=dia/2, radius2=dia/2, depth=(z1-z0))
    bmesh.ops.translate(bm, vec=(cx, cy, (z0+z1)/2), verts=bm.verts)
    return _finish(name, bm, m, c or bpy.context.scene.collection)

def cylx(name, cy, cz, x0, x1, dia, m=None, c=None, seg=32):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=dia/2, radius2=dia/2, depth=(x1-x0))
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(math.radians(90), 3, 'Y'), verts=bm.verts)
    bmesh.ops.translate(bm, vec=((x0+x1)/2, cy, cz), verts=bm.verts)
    return _finish(name, bm, m, c or bpy.context.scene.collection)

def boolean(target, cutter, op='DIFFERENCE'):
    md = target.modifiers.new('bool', 'BOOLEAN')
    md.operation = op
    md.solver = 'EXACT'
    md.object = cutter
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = target
    target.select_set(True)
    bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(cutter, do_unlink=True)

def join(objs, name):
    objs = [o for o in objs if o.name in bpy.data.objects]
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = name
    return obj

def inter_vol(src, other, dz=0.0, dy=0.0, dx=0.0):
    dup = src.copy(); dup.data = src.data.copy()
    bpy.context.scene.collection.objects.link(dup)
    dup.location = (src.location.x+dx, src.location.y+dy, src.location.z+dz)
    md = dup.modifiers.new('int', 'BOOLEAN')
    md.operation = 'INTERSECT'; md.solver = 'EXACT'; md.object = other
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = dup
    dup.select_set(True)
    bpy.ops.object.modifier_apply(modifier=md.name)
    bm = bmesh.new(); bm.from_mesh(dup.data)
    vol = abs(bm.calc_volume()); bm.free()
    bpy.data.objects.remove(dup, do_unlink=True)
    return vol

def nonmanifold(obj):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    n = sum(1 for e in bm.edges if not e.is_manifold)
    bm.free()
    return n

def wbbox(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))

def cyly(name, cx, cz, y0, y1, dia, m=None, c=None, seg=32):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=dia/2, radius2=dia/2, depth=(y1-y0))
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(cx, (y0+y1)/2, cz), verts=bm.verts)
    return _finish(name, bm, m, c or bpy.context.scene.collection)
