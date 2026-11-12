import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
def bvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
def mindist(a,b,label,step=1):
    tb=bvh(b); bm=bmesh.new(); bm.from_mesh(a.data); bm.transform(a.matrix_world); bm.verts.ensure_lookup_table()
    best=1e9
    for i in range(0,len(bm.verts),step):
        p=bm.verts[i].co; loc,nor,idx,d=tb.find_nearest(p)
        if loc is not None and d<best: best=d
    bm.free(); print(f"DIST {label:36s} {best:.3f}")
lid=bpy.data.objects['Enclosure_Lid']; ring=bpy.data.objects['LED_Diffuser_Ring']
for n in ('PCB_Board','PCB_Components','OLED_1p3_Module','OLED_ActiveArea','Battery_103450','Speaker_3070','Face_Plate','Touch_Module_Fit'):
    o=bpy.data.objects[n]
    t1,t2=bvh(lid),bvh(o); n1=len(t1.overlap(t2))
    t3=bvh(ring); n2=len(t3.overlap(t2))
    print(f"PAIR Lid x {n:22s} {n1:4d}   Ring x {n:22s} {n2:4d}")
    mindist(lid,o,f"Lid->{n}",2)
# lid vertical sweep vs body
body=bpy.data.objects['Enclosure_Body']; tb=bvh(body)
bm=bmesh.new(); bm.from_mesh(lid.data); bm.transform(lid.matrix_world)
import copy
for dz in (0,1,2,4,8,16,30):
    bm2=bm.copy()
    for v in bm2.verts: v.co.z += dz
    t=BVHTree.FromBMesh(bm2); bm2.free()
    print(f"LIDSWEEP +{dz:2d}mm overlap(body)={len(t.overlap(tb))}")
bm.free()
