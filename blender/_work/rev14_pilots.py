import bpy, bmesh, math
from mathutils import Vector

BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
body = bpy.data.objects['Enclosure_Body']
col = bpy.data.collections['RobotDog_v3']

FRONT = [(20.8,25.5),(-20.8,25.5),(20.8,54.5),(-20.8,54.5)]
BOTTOM = [(20,30),(-20,30),(20,-50),(-20,-50),(20,48),(-20,48)]
SEG = 64

def mesh_obj(name, verts, faces):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate(); me.update()
    o = bpy.data.objects.new(name, me); col.objects.link(o)
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me); bm.free(); me.update()
    return o

def lathe(rings, axis, center, seg=SEG):
    """rings: list of (r, d) along axis; returns closed solid verts/faces."""
    V=[]; F=[]
    for (r,d) in rings:
        for i in range(seg):
            a = 2*math.pi*i/seg
            c, s = math.cos(a)*r, math.sin(a)*r
            if axis == 'Z':
                V.append((center[0]+c, center[1]+s, d))
            else:
                V.append((center[0]+c, d, center[1]+s))
    nr = len(rings)
    for k in range(nr-1):
        b0 = k*seg; b1 = (k+1)*seg
        for i in range(seg):
            j = (i+1) % seg
            F.append((b0+i, b0+j, b1+j, b1+i))
    F.append(tuple(range(seg)))                       # cap at first ring
    F.append(tuple((nr-1)*seg+i for i in range(seg-1, -1, -1)))
    return V, F

V=[]; F=[]
for (x,z) in FRONT:
    v,f = lathe([(0.97, 61.79), (0.97, 57.50)], 'Y', (x,z))
    off=len(V); V += v; F += [tuple(i+off for i in q) for q in f]
for (x,y) in BOTTOM:
    v,f = lathe([(0.97, 20.02), (0.97, 31.60)], 'Z', (x,y))
    off=len(V); V += v; F += [tuple(i+off for i in q) for q in f]
fill = mesh_obj('PilotFill', V, F)

V=[]; F=[]
for (x,z) in FRONT:
    v,f = lathe([(1.25, 62.00), (1.25, 61.80), (0.85, 61.40), (0.85, 57.30)], 'Y', (x,z))
    off=len(V); V += v; F += [tuple(i+off for i in q) for q in f]
for (x,y) in BOTTOM:
    v,f = lathe([(1.25, 19.90), (1.25, 20.00), (0.85, 20.40), (0.85, 31.60)], 'Z', (x,y))
    off=len(V); V += v; F += [tuple(i+off for i in q) for q in f]
drill = mesh_obj('PilotDrill', V, F)

def boolean(target, cutter, op):
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True); bpy.context.view_layer.objects.active = target
    m = target.modifiers.new('bool', 'BOOLEAN'); m.operation = op; m.solver = 'EXACT'; m.object = cutter
    bpy.ops.object.modifier_apply(modifier=m.name)

print('FILL', len(fill.data.vertices), len(fill.data.polygons))
print('DRILL', len(drill.data.vertices), len(drill.data.polygons))
boolean(body, fill, 'UNION')
bpy.data.objects.remove(fill, do_unlink=True)
boolean(body, drill, 'DIFFERENCE')
bpy.data.objects.remove(drill, do_unlink=True)

bm = bmesh.new(); bm.from_mesh(body.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
bm.to_mesh(body.data); bm.free(); body.data.update()
bpy.context.view_layer.update()

bm = bmesh.new(); bm.from_mesh(body.data)
print(f"BODY v={len(bm.verts)} f={len(bm.faces)} nm={sum(1 for e in bm.edges if len(e.link_faces)!=2)} "
      f"bnd={sum(1 for e in bm.edges if len(e.link_faces)<2)} zero={sum(1 for f in bm.faces if f.calc_area()<1e-9)} "
      f"vol={bm.calc_volume(signed=True):.1f}")
bm.free()

def world_ray(origin, direction):
    mw = body.matrix_world; inv = mw.inverted()
    hit, loc, nor, idx = body.ray_cast(inv @ Vector(origin), (inv.to_3x3() @ Vector(direction)).normalized(), distance=500)
    if not hit: return None
    return mw @ loc, (mw.to_3x3().inverted().transposed() @ nor).normalized()

print("front hole (20.8,25.5) ray -Y: dx -> first y")
for dx in (0,0.5,0.8,0.84,0.85,0.86,0.9,1.0,1.1,1.2,1.3):
    r = world_ray((20.8+dx,80,25.5),(0,-1,0))
    print(f"  dx={dx:.2f} -> {None if not r else round(r[0].y,3)}")
print("front bottom: ray -Y at dx=0 -> y")
r = world_ray((20.8,80,25.5),(0,-1,0)); print('  ', None if not r else round(r[0].y,3))
print("bottom hole (20,30) ray +Z: d -> first z")
for d in (0,0.5,0.8,0.84,0.85,0.86,0.9,1.0,1.1,1.2,1.3):
    r = world_ray((20+d,30,10),(0,0,1))
    print(f"  d={d:.2f} -> {None if not r else round(r[0].z,3)}")

bpy.ops.wm.save_mainfile(filepath=BLEND)
print('SAVED', BLEND)
