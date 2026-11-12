import bpy, bmesh
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
sc=bpy.context.scene
def inter(a,b):
    A=bpy.data.objects[a]; B=bpy.data.objects[b]
    da=A.copy(); da.data=A.data.copy(); sc.collection.objects.link(da)
    db=B.copy(); db.data=B.data.copy(); sc.collection.objects.link(db)
    for m in list(da.modifiers): da.modifiers.remove(m)
    for m in list(db.modifiers): db.modifiers.remove(m)
    bpy.context.view_layer.objects.active=da
    md=da.modifiers.new('i','BOOLEAN'); md.operation='INTERSECT'; md.solver='EXACT'; md.object=db
    bpy.ops.object.modifier_apply(modifier=md.name)
    bm=bmesh.new(); bm.from_mesh(da.data)
    vol=bm.calc_volume(signed=True) if bm.faces else 0
    xs=[v.co.x for v in bm.verts]; ys=[v.co.y for v in bm.verts]; zs=[v.co.z for v in bm.verts]
    print(f'INTERSECT {a} x {b}: v={len(bm.verts)} f={len(bm.faces)} vol={vol:.4f} '
          f'bbox x[{min(xs) if xs else 0:.2f},{max(xs) if xs else 0:.2f}] y[{min(ys) if ys else 0:.2f},{max(ys) if ys else 0:.2f}] z[{min(zs) if zs else 0:.2f},{max(zs) if zs else 0:.2f}]')
    bm.free()
    bpy.data.objects.remove(da,do_unlink=True); bpy.data.objects.remove(db,do_unlink=True)
for a,b in [('Enclosure_Lid','Enclosure_Body'),('Face_Plate','Enclosure_Body'),('Belly_Pan','Enclosure_Body'),
            ('LED_Diffuser_Ring','Enclosure_Lid'),('Tail','Enclosure_Lid'),('Ear_R','Enclosure_Lid'),
            ('Button_Top_2','Enclosure_Lid')]:
    inter(a,b)
