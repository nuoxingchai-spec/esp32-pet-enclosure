import bpy, bmesh, math
from mathutils import Vector

FINAL = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v2.blend"
OUT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage5a.blend"
bpy.ops.wm.open_mainfile(filepath=FINAL)

BODY = bpy.data.objects['Enclosure_Body']
LID = bpy.data.objects['Enclosure_Lid']

def act(o):
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o

def apply_all(o):
    act(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

def cyl(name, r, z0, z1, x=0.0, y=0.0, verts=96, axis='Z'):
    d = z1 - z0
    if axis == 'Z':
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d, location=(x, y, (z0+z1)/2))
    elif axis == 'X':
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d, location=((z0+z1)/2, y, x), rotation=(0, math.pi/2, 0))
    o = bpy.context.object; o.name = name
    apply_all(o)
    return o

def box(name, sx, sy, sz, x=0.0, y=0.0, z=0.0, rotz=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    o = bpy.context.object; o.name = name
    o.scale = (sx, sy, sz)
    act(o); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rotz:
        o.rotation_euler[2] = rotz
        act(o); bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    act(o); bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    return o

def bevel(o, width=0.5, segments=3):
    act(o)
    m = o.modifiers.new('bev', 'BEVEL')
    m.width = width; m.segments = segments; m.limit_method = 'ANGLE'; m.angle_limit = math.radians(30)
    bpy.ops.object.modifier_apply(modifier=m.name)

def boolean(target, cutter, op='DIFFERENCE', solver='EXACT'):
    bpy.context.view_layer.update()
    act(target)
    m = target.modifiers.new('bool', 'BOOLEAN')
    m.operation = op; m.solver = solver; m.object = cutter
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)

def clean(o, dist=0.0005):
    act(o)
    me = o.data
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=dist)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    me.update()

# ---------- A. remove old side buttons, fill side holes ----------
for i in range(1, 4):
    ob = bpy.data.objects.get(f'Button_Plunger_{i}')
    if ob: bpy.data.objects.remove(ob, do_unlink=True)

for y in (-35.47, -42.45, -49.47):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=2.15, depth=3.55,
        location=(-37.225, y, 57.2), rotation=(0, math.pi/2, 0))
    plug = bpy.context.object; plug.name = 'SidePlug'
    apply_all(plug)
    boolean(BODY, plug, 'UNION')

clean(BODY)
print('BODY after plugs: verts', len(BODY.data.vertices), 'polys', len(BODY.data.polygons))

# ---------- B. lid: fill touch hole, C-clip, slits, button holes, ear/tail slots ----------
# 1) fill old round touch opening (r8 disk, top 0.02 below lid top)
fill = cyl('TouchFill', 8.0, 64.6, 66.98, 0, 35)
boolean(LID, fill, 'UNION')

# 2) C-shaped touch retainer under the ceiling
outer = cyl('TouchOuter', 7.4, 62.25, 64.9, 0, 35)
inner = cyl('TouchInner', 6.1, 62.15, 65.0, 0, 35)
boolean(outer, inner, 'DIFFERENCE')
opening = box('TouchOpening', 13.0, 8.0, 3.0, 0, 42.8, 63.55)
boolean(outer, opening, 'DIFFERENCE')
# 4 bottom lips at 30/150/210/330 deg
for ang in (30, 150, 210, 330):
    a = math.radians(ang)
    rr = 5.8
    lp = box('Lip', 0.6, 2.2, 0.30, rr*math.cos(a), 35 + rr*math.sin(a), 62.40, rotz=a)
    boolean(outer, lp, 'UNION')
boolean(LID, outer, 'UNION')

# 3) shallow finger recess + 3 slits
recess = cyl('FingerRecess', 6.5, 66.0, 67.2, 0, 35)
boolean(LID, recess, 'DIFFERENCE')
for xs in (-3.2, 0.0, 3.2):
    slot = box('Slot', 1.2, 7.0, 2.7, xs, 35, 65.95)
    e1 = cyl('SlotEnd', 0.6, 64.55, 67.2, xs, 35 - 3.5)
    e2 = cyl('SlotEnd', 0.6, 64.55, 67.2, xs, 35 + 3.5)
    boolean(slot, e1, 'UNION'); boolean(slot, e2, 'UNION')
    boolean(LID, slot, 'DIFFERENCE')

# 4) top button holes + shallow head seat, aligned with the 3 PCB switches
for y in (-35.47, -42.45, -49.47):
    hole = cyl('BtnHole', 2.10, 64.2, 67.2, -24.83, y)
    boolean(LID, hole, 'DIFFERENCE')
    seat = cyl('BtnSeat', 2.45, 66.70, 67.2, -24.83, y)
    boolean(LID, seat, 'DIFFERENCE')
    # lead-in at the inner ceiling mouth so the split cap can squeeze in
    bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=2.55, radius2=2.10, depth=0.4,
                                    location=(-24.83, y, 64.8))
    lead = bpy.context.object; lead.name = 'BtnLead'
    apply_all(lead)
    boolean(LID, lead, 'DIFFERENCE')

# 5) ear slots (10.4 along Y x 3.8 along X) and tail slot (10.4 X x 6.4 Y)
for x in (-21.0, 21.0):
    es = box('EarSlot', 9.6, 3.8, 3.0, x, 30, 65.7)
    boolean(LID, es, 'DIFFERENCE')
ts = box('TailSlot', 10.4, 6.7, 3.0, 0, -43, 65.7)
boolean(LID, ts, 'DIFFERENCE')

clean(LID, 0.0003)
print('LID after cuts: verts', len(LID.data.vertices), 'polys', len(LID.data.polygons))

# move touch module down under the new ceiling
tm = bpy.data.objects['Touch_Module_Fit']
tm.location.z -= 2.02
print('TOUCH loc', tuple(round(v,2) for v in tm.location))

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print('SAVED', OUT)
