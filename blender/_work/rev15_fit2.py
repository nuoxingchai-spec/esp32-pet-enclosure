import bpy, bmesh
from mathutils import Vector
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
dg = bpy.context.evaluated_depsgraph_get()
def world_bm(name):
    o=bpy.data.objects[name]; bm=bmesh.new()
    ev=o.evaluated_get(dg); me=ev.to_mesh(); bm.from_mesh(me); bm.transform(o.matrix_world)
    ev.to_mesh_clear(); return bm
def overlap(a,b):
    A=world_bm(a); B=world_bm(b)
    t=__import__('mathutils').bvhtree.BVHTree.FromBMesh(A)
    hits=[]
    for f in B.faces:
        c=f.calc_center_median()
        loc,nor,idx,d=t.ray_cast(c, f.normal, 20.0)
        if loc is not None:
            # inside test: cast both ways count parity
            cnt=0; o=c.copy(); dirv=f.normal.copy()
            for _ in range(8):
                loc,nor,idx,d=t.ray_cast(o,dirv,200)
                if loc is None: break
                cnt+=1; o=loc+dirv*0.001
            if cnt%2==1: hits.append(c)
    A.free(); B.free()
    return hits
pairs=[('Button_Top_1','PCB_Components'),('Button_Top_2','PCB_Components'),('Button_Top_3','PCB_Components'),
       ('Button_Top_1','PCB_Board'),('Button_Top_2','PCB_Board'),('Button_Top_3','PCB_Board'),
       ('Touch_Module_Fit','Enclosure_Lid'),('Touch_Module_Fit','PCB_Components'),
       ('Button_Top_2','Touch_Module_Fit')]
for a,b in pairs:
    h=overlap(a,b)
    print(f"OVL {a} x {b}: {len(h)}", (round(min(p.z for p in h),2),round(max(p.z for p in h),2)) if h else '')
# servo top cover: cast down from above inside bay footprint, does body material exist between 44.1 and 58?
body=bpy.data.objects['Enclosure_Body']; mw=body.matrix_world; inv=mw.inverted()
print('--- body material above servo top (44.1) within bay footprint ---')
for sy in (1,-1):
  for ys in (33,40,44,50,55):
    hits=[]
    for x in (15,20,25,30,35):
        for z in (44.2,46,48,50):
            ok,loc,nor,idx=body.ray_cast(inv@Vector((x,sy*ys,z)),(inv.to_3x3()@Vector((0,0,1))).normalized(),distance=60,depsgraph=dg)
            # only count if leaving bay upward? skip
    print(' skip')
# simpler: BVH count body faces inside bay slab
bm=bmesh.new(); bm.from_mesh(body.data); bm.transform(body.matrix_world)
import mathutils
t=mathutils.bvhtree.BVHTree.FromBMesh(bm)
# cast down from z57 at grid over front-right bay, count body hits above 44.6
for sy in (1,-1):
    pts=[]
    for x in range(15,37,3):
        for y in (30,36,42,48,54,58):
            loc,nor,idx,d=t.ray_cast(Vector((x,sy*y,57.5)),Vector((0,0,-1)),60)
            if loc is not None and loc.z>44.3:
                pts.append((round(x),sy*y,round(loc.z,1)))
    print('bay', sy, 'top-material pts:', pts[:20], 'n=',len(pts))
bm.free()
