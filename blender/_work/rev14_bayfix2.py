import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
body = bpy.data.objects['Enclosure_Body']
col = bpy.data.collections['RobotDog_v3']
def make_box(name, boxes):
    bm = bmesh.new()
    for (x0,x1,y0,y1,z0,z1) in boxes:
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r['verts']:
            v.co.x=x0+(v.co.x+0.5)*(x1-x0); v.co.y=y0+(v.co.y+0.5)*(y1-y0); v.co.z=z0+(v.co.z+0.5)*(z1-z0)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(name,me); col.objects.link(o); return o
cuts=[]; adds=[]
for sx in (1,-1):
    for sy in (1,-1):
        x0,x1=(14.0,36.5) if sx>0 else (-36.5,-14.0)
        y0,y1=(27.6,60.4) if sy>0 else (-60.4,-27.6)
        cuts.append((x0,x1,y0,y1,31.8,33.0))
        adds.append((x0,x1,y0,y1,30.9,31.9))
cut=make_box('BayCut', pads=cuts) if False else make_box('BayCut', cuts)
add=make_box('BayAdd', adds)
def boolean(target, cutter, op):
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True); bpy.context.view_layer.objects.active=target
    m=target.modifiers.new('b','BOOLEAN'); m.operation=op; m.solver='EXACT'; m.object=cutter
    bpy.ops.object.modifier_apply(modifier=m.name)
boolean(body,cut,'DIFFERENCE'); bpy.data.objects.remove(cut,do_unlink=True)
boolean(body,add,'UNION'); bpy.data.objects.remove(add,do_unlink=True)
bm=bmesh.new(); bm.from_mesh(body.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
bm.to_mesh(body.data); bm.free(); body.data.update(); bpy.context.view_layer.update()
bm=bmesh.new(); bm.from_mesh(body.data)
print(f"BODY v={len(bm.verts)} f={len(bm.faces)} nm={sum(1 for e in bm.edges if len(e.link_faces)!=2)} "
      f"bnd={sum(1 for e in bm.edges if len(e.link_faces)<2)} zero={sum(1 for f in bm.faces if f.calc_area()<1e-9)} "
      f"vol={bm.calc_volume(signed=True):.1f}")
bm.free()
bm=bmesh.new(); bm.from_mesh(body.data); bm.transform(body.matrix_world); tb=BVHTree.FromBMesh(bm); bm.free()
for sx in (1,-1):
    for sy in (1,-1):
        X=(14.1,36.6) if sx>0 else (-36.6,-14.1); Y=(32.6,55.4) if sy>0 else (-55.4,-32.6)
        for sh in (0.0,0.2):
            bm3=bmesh.new(); bmesh.ops.create_cube(bm3,size=1.0)
            for v in bm3.verts:
                v.co.x=X[0]+sh+(v.co.x+0.5)*((X[1]-X[0])-2*sh)
                v.co.y=Y[0]+sh+(v.co.y+0.5)*((Y[1]-Y[0])-2*sh)
                v.co.z=31.9+sh+(v.co.z+0.5)*((44.1-31.9)-2*sh)
            t3=BVHTree.FromBMesh(bm3); bm3.free()
            print(f"SERVOBOX {sx:+d}{sy:+d} shrink={sh} overlap={len(tb.overlap(t3))}")
bpy.ops.wm.save_mainfile(filepath=BLEND)
print('SAVED')
