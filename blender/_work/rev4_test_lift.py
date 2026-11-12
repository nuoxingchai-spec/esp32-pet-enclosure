import bpy, bmesh, math
from mathutils import Vector
F = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev4_test_cut.blend"
bpy.ops.wm.open_mainfile(filepath=F)
sc = bpy.context.scene
ob = bpy.data.objects['BODY_TEST']
mw = ob.matrix_world; mi = mw.inverted(); M3 = mw.to_3x3(); M3i = M3.inverted()
dg = bpy.context.evaluated_depsgraph_get()
H = 0.20
ZSEAM = 54.35

bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(mw)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()

def is_sliver(f):
    zs=[v.co.z for v in f.verts]
    return min(zs)>ZSEAM-0.05 and max(zs)<ZSEAM+0.05 and f.normal.z>0.9

ups=[]
for v in bm.verts:
    if abs(v.co.z-ZSEAM)>0.02: continue
    above=any((not is_sliver(f)) and max(x.co.z for x in f.verts)>ZSEAM+0.05 for f in v.link_faces)
    below=any((not is_sliver(f)) and min(x.co.z for x in f.verts)<ZSEAM-0.05 for f in v.link_faces)
    if above and not below: ups.append(v)
print('UP verts', len(ups))
moved=0; miss=0
for v in ups:
    d = Vector((v.co.x, v.co.y, 0.0))
    if d.length < 1e-6: miss+=1; continue
    d.normalize()
    org = mi @ Vector((v.co.x + 12.0*d.x, v.co.y + 12.0*d.y, ZSEAM-0.01))
    ok, loc, nor, idx = ob.ray_cast(org, (M3i @ (-d)).normalized(), distance=40.0, depsgraph=dg)
    if not ok:
        miss+=1; continue
    p = mw @ loc
    v.co.x = p.x; v.co.y = p.y; v.co.z = ZSEAM + H
    moved+=1
print('moved', moved, 'miss', miss)

bm.normal_update()
# check lifted fan faces orientation
bad=0; fan=0
for f in bm.faces:
    zs=[v.co.z for v in f.verts]
    if min(zs) > ZSEAM-0.01 and max(zs) < ZSEAM+H+0.01:
        c=f.calc_center_median(); r=Vector((c.x,c.y,0))
        if r.length>1e-6 and f.normal.dot(r.normalized()) < -0.2:
            bad+=1
        fan+=1
print('fan faces', fan, 'inward normals', bad)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(ob.data); bm.free(); ob.data.update()

# audit
bm2 = bmesh.new(); bm2.from_mesh(ob.data); bm2.transform(mw)
nm = sum(1 for e in bm2.edges if len(e.link_faces)!=2)
bnd = sum(1 for e in bm2.edges if len(e.link_faces)<2)
zero = sum(1 for f in bm2.faces if f.calc_area()<1e-9)
bm2.free()
print('AUDIT v',len(ob.data.vertices),'f',len(ob.data.polygons),'nm',nm,'bnd',bnd,'zero',zero)

# A/B renders: original hidden body vs test body, same cams
body = bpy.data.objects['Enclosure_Body']
cut = bpy.data.objects.get('Cutter_test')
if cut: cut.hide_render=True
cam = bpy.data.objects.get('C')
def shot(path):
    sc.render.filepath=path; bpy.ops.render.render(write_still=True)
ob.hide_render=True; body.hide_render=False
shot(r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev4_orig_corner.png")
shot(r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev4_orig_side.png")
body.hide_render=True; ob.hide_render=False
shot(r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev4_lift_corner.png")
shot(r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev4_lift_side.png")
bpy.ops.wm.save_as_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev4_test_lift.blend")
print('DONE')
