import bpy, bmesh
from mathutils import Vector
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
body = bpy.data.objects['Enclosure_Body']
col = bpy.data.collections['RobotDog_v3']
bm2 = bmesh.new()
for sx in (1,-1):
    for sy in (1,-1):
        x0,x1 = (26.0,36.5) if sx>0 else (-36.5,-26.0)
        y0,y1 = (27.6,60.4) if sy>0 else (-60.4,-27.6)
        r = bmesh.ops.create_cube(bm2, size=1.0)
        for v in r['verts']:
            v.co.x = x0 + (v.co.x+0.5)*(x1-x0)
            v.co.y = y0 + (v.co.y+0.5)*(y1-y0)
            v.co.z = 31.6 + (v.co.z+0.5)*(32.9-31.6)
me = bpy.data.meshes.new('BayFloorCut')
bm2.to_mesh(me); bm2.free()
cut = bpy.data.objects.new('BayFloorCut', me); col.objects.link(cut)
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True); bpy.context.view_layer.objects.active = body
m = body.modifiers.new('bool','BOOLEAN'); m.operation='DIFFERENCE'; m.solver='EXACT'; m.object=cut
bpy.ops.object.modifier_apply(modifier=m.name)
bpy.data.objects.remove(cut, do_unlink=True)
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
# verify servo body fits
from mathutils.bvhtree import BVHTree
bm = bmesh.new(); bm.from_mesh(body.data); bm.transform(body.matrix_world); tb=BVHTree.FromBMesh(bm); bm.free()
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
