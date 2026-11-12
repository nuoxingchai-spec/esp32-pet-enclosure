import bpy, bmesh, math
from mathutils import Vector

BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
sc = bpy.context.scene
col = bpy.data.collections['RobotDog_v3']

def act(o):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o

def apply_all(o):
    act(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

def box(name, sx, sy, sz, x=0.0, y=0.0, z=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    o = bpy.context.object; o.name = name; o.scale = (sx, sy, sz)
    act(o); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    act(o); bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    return o

def bevel(o, width=0.5, segments=3):
    act(o); m = o.modifiers.new('bev', 'BEVEL'); m.width = width; m.segments = segments
    m.limit_method = 'ANGLE'; m.angle_limit = math.radians(30)
    bpy.ops.object.modifier_apply(modifier=m.name)

def boolean(target, cutter, op='DIFFERENCE'):
    bpy.context.view_layer.update(); act(target)
    m = target.modifiers.new('bool', 'BOOLEAN'); m.operation = op; m.solver = 'EXACT'; m.object = cutter
    bpy.ops.object.modifier_apply(modifier=m.name); bpy.data.objects.remove(cutter, do_unlink=True)

def clean(o, dist=0.0004):
    act(o); bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=dist)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data); bm.free(); o.data.update()

# tongue + flange unchanged
tt = box('TailTongue', 10.2, 6.4, 3.4, 0, 0, 1.7)
bevel(tt, 0.5, 2)
tflare = box('TailFlare', 13.0, 9.0, 1.4, 0, 0, 4.0)
bevel(tflare, 0.7, 3)
tail = tt
boolean(tail, tflare, 'UNION')

# longer, flattened curved tube
cu = bpy.data.curves.new('TailCurve','CURVE'); cu.dimensions='3D'; cu.resolution_u=24
cu.bevel_depth=1.0; cu.bevel_resolution=8; cu.use_fill_caps=True
sp = cu.splines.new('BEZIER')
pts = [(0.0, 3.5, 3.05), (-1.6, 8.2, 2.98), (-4.1, 13.4, 2.82),
       (-7.3, 18.0, 2.60), (-10.9, 21.7, 2.34), (-14.2, 24.6, 2.06),
       (-16.1, 26.9, 1.78)]
sp.bezier_points.add(len(pts)-1)
for bp, (y, z, r) in zip(sp.bezier_points, pts):
    bp.co = (0, y, z); bp.radius = r
    bp.handle_left_type = 'AUTO'; bp.handle_right_type = 'AUTO'
tob = bpy.data.objects.new('TailTube', cu); sc.collection.objects.link(tob)
bpy.ops.object.select_all(action='DESELECT'); tob.select_set(True); bpy.context.view_layer.objects.active = tob
bpy.ops.object.convert(target='MESH')
tailtube = bpy.context.object
# flatten to an ellipse with X thickness = 0.82 * YZ width
act(tailtube); tailtube.scale[0] = 0.82
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
boolean(tail, tailtube, 'UNION')
print('TAIL after tube', len(tail.data.vertices), tuple(round(v,2) for v in tail.dimensions))

# flattened ball tip
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1.78, location=(0,-16.1,26.9))
tip = bpy.context.object; tip.name = 'TailTip'; act(tip)
tip.scale[0] = 0.82
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
boolean(tail, tip, 'UNION')

clean(tail)
act(tail)
try:
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
except Exception as e:
    print('SMOOTH tail skipped', e)
print('TAIL', len(tail.data.vertices), 'verts', 'dims', tuple(round(v,3) for v in tail.dimensions))

bm = bmesh.new(); bm.from_mesh(tail.data)
print('TAIL audit comps', len([v for v in [] ]))
print('TAIL nm', sum(1 for e in bm.edges if len(e.link_faces) != 2),
      'bnd', sum(1 for e in bm.edges if len(e.link_faces) < 2),
      'zero', sum(1 for f in bm.faces if f.calc_area() < 1e-9),
      'vol', round(bm.calc_volume(signed=True),1), 'faces', len(bm.faces))
bm.free()
bb = [tail.matrix_world @ Vector(c) for c in tail.bound_box]
print('TAIL bb', tuple(round(min(p[i] for p in bb),2) for i in range(3)),
      tuple(round(max(p[i] for p in bb),2) for i in range(3)))

new_mesh = tail.data
new_mesh.name = 'Tail_new'
placed = bpy.data.objects['Tail']
master = bpy.data.objects['Tail_Master']
old = placed.data
placed.data = new_mesh
master.data = new_mesh
bpy.data.objects.remove(tail, do_unlink=True)
old.name = 'Tail_old'
bpy.data.meshes.remove(old)
new_mesh.name = 'Tail'
# keep master hidden
master.hide_render = True; master.hide_set(True); master.hide_viewport = True
bpy.context.view_layer.update()
for o in (placed, master):
    print('OBJ', o.name, 'dims', tuple(round(v,3) for v in o.dimensions))
print('MASTER/LOC', tuple(round(v,2) for v in placed.location), tuple(round(v,2) for v in master.location))
bpy.ops.wm.save_mainfile(filepath=BLEND)
print('SAVED', BLEND)
