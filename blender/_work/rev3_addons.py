import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler

IN = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage5a.blend"
OUT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage5b.blend"
bpy.ops.wm.open_mainfile(filepath=IN)
COL = bpy.data.collections['RobotDog_v2']

def act(o):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
def apply_all(o):
    act(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
def cyl(name, r, z0, z1, x=0.0, y=0.0, verts=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=z1-z0, location=(x, y, (z0+z1)/2))
    o = bpy.context.object; o.name = name; apply_all(o); return o
def box(name, sx, sy, sz, x=0.0, y=0.0, z=0.0, rotz=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    o = bpy.context.object; o.name = name; o.scale = (sx, sy, sz)
    act(o); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rotz:
        o.rotation_euler[2] = rotz
        act(o); bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
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
def to_col(o, col=COL):
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o)
def make_master(o, name, color, hide=True):
    o.name = name; o.data.name = name; o.color = color; to_col(o)
    o.hide_render = hide; o.hide_set(hide); o.hide_viewport = hide
    return o

# ================= BUTTON =================
parts = []
flange = cyl('BtnFlange', 2.8, 0.0, 1.0)
shaft = cyl('BtnShaft', 1.8, 0.95, 8.2)
cap = cyl('BtnCap', 2.3, 8.15, 8.85, verts=64)
bevel(cap, 0.45, 3)
for p in (flange, shaft, cap): parts.append(p)
base = parts[0]
for p in parts[1:]: boolean(base, p, 'UNION')
# 4 relief slots in cap
for ang in (45, 135, 225, 315):
    a = math.radians(ang); rr = 1.55
    sl = box('BtnSlot', 1.9, 0.5, 0.95, rr*math.cos(a), rr*math.sin(a), 8.55, rotz=a)
    boolean(base, sl, 'DIFFERENCE')
clean(base)
act(base)
try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
except Exception as e: print('SMOOTH base skipped', e)
base.name = 'Button_Top_Master'; base.data.name = 'Button_Top'
print('BUTTON', len(base.data.vertices), 'verts', 'dims', tuple(round(v,3) for v in base.dimensions))

# ================= EAR (right master) =================
tongue = box('EarTongue', 9.4, 3.6, 3.4, 0, 0, 1.7)
bevel(tongue, 0.4, 2)
flare = box('EarFlare', 11.5, 7.5, 1.4, 0, 0, 4.0)
bevel(flare, 0.6, 3)
fin = box('EarFin', 8.5, 3.0, 12.0, 0, 0, 10.2)
# taper to a rounded ear top
act(fin)
for v in fin.data.vertices:
    if v.co.z > 15.2:
        v.co.x *= 0.40; v.co.y *= 0.70
bevel(fin, 1.15, 4)
# lean outward 14 deg, back 6 deg around the root
piv = Vector((0,0,4.4))
M = Matrix.Translation(piv) @ Euler((math.radians(-6), math.radians(14), 0)).to_matrix().to_4x4() @ Matrix.Translation(-piv)
act(fin)
for v in fin.data.vertices: v.co = M @ v.co
ear = tongue
for p in (flare, fin): boolean(ear, p, 'UNION')
clean(ear)
act(ear)
try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
except Exception as e: print('SMOOTH ear skipped', e)
ear.name = 'Ear_R_Master'; ear.data.name = 'Ear_R'
print('EAR', len(ear.data.vertices), 'verts', 'dims', tuple(round(v,3) for v in ear.dimensions))
# mirrored left master
earL = ear.copy(); earL.data = ear.data.copy(); earL.data.name = 'Ear_L'
to_col(earL); act(earL)
for v in earL.data.vertices: v.co.x *= -1.0
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
# flip normals after mirror
act(earL); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
act(earL)
try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
except Exception as e: print('SMOOTH earL skipped', e)
earL.name = 'Ear_L_Master'; earL.data.name = 'Ear_L'
print('EARL', len(earL.data.vertices), 'verts', 'dims', tuple(round(v,3) for v in earL.dimensions))

# ================= TAIL =================
tt = box('TailTongue', 10.2, 6.4, 3.4, 0, 0, 1.7)
bevel(tt, 0.5, 2)
tflare = box('TailFlare', 13.0, 9.0, 1.4, 0, 0, 4.0)
bevel(tflare, 0.7, 3)
tail = tt
boolean(tail, tflare, 'UNION')
# curved tail tube, root buried in the flare, round tip
cu = bpy.data.curves.new('TailCurve','CURVE'); cu.dimensions='3D'; cu.resolution_u=16
cu.bevel_depth=1.0; cu.bevel_resolution=6; cu.use_fill_caps=True
sp = cu.splines.new('BEZIER'); pts=[(0.0,3.7,2.7),(-1.6,8.6,2.6),(-3.8,13.1,2.45),(-6.8,16.4,2.2),(-10.0,18.4,1.9),(-12.8,19.1,1.55)]
sp.bezier_points.add(len(pts)-1)
for bp,(y,z,r) in zip(sp.bezier_points,pts):
    bp.co=(0,y,z); bp.radius=r; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
tob = bpy.data.objects.new('TailTube', cu); COL.objects.link(tob)
bpy.context.view_layer.objects.active=tob
bpy.ops.object.select_all(action='DESELECT'); tob.select_set(True)
bpy.ops.object.convert(target='MESH')
tailtube = bpy.context.object
boolean(tail, tailtube, 'UNION')
print('TAIL after tube', len(tail.data.vertices), tuple(round(v,2) for v in tail.dimensions))
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1.55, location=(0,-12.8,19.1))
tip = bpy.context.object; tip.name = 'TailTip'; apply_all(tip)
boolean(tail, tip, 'UNION')
print('TAIL after tip', len(tail.data.vertices), tuple(round(v,2) for v in tail.dimensions))
clean(tail)
act(tail)
try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
except Exception as e: print('SMOOTH tail skipped', e)
tail.name='Tail_Master'; tail.data.name='Tail'
print('TAIL', len(tail.data.vertices), 'verts', 'dims', tuple(round(v,3) for v in tail.dimensions))

# ================= MASTERS + ASSEMBLY =================
mm = bpy.data.collections.new('Print_Masters'); bpy.context.scene.collection.children.link(mm)
for o,n in ((base,'Button_Top_Master'),(ear,'Ear_R_Master'),(earL,'Ear_L_Master'),(tail,'Tail_Master')):
    for c in list(o.users_collection): c.objects.unlink(o)
    mm.objects.link(o); o.hide_render=True; o.hide_set(True); o.hide_viewport=True
    o.color = (0.93,0.93,0.90,1) if o.name.startswith('Button') else (0.78,0.62,0.43,1)

def place(src, name, x, y, z):
    o=src.copy(); to_col(o); o.name=name
    o.location=(x,y,z); o.hide_render=False; o.hide_set(False); o.hide_viewport=False
    o.color=src.color
    return o
for i,y in enumerate((-35.47,-42.45,-49.47),1):
    place(base, f'Button_Top_{i}', -24.83, y, 58.9)
place(ear, 'Ear_R', 21.0, 30.0, 63.72)
place(earL, 'Ear_L', -21.0, 30.0, 63.72)
place(tail, 'Tail', 0.0, -43.0, 63.72)

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print('SAVED', OUT)
