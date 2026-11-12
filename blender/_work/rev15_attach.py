import bpy, bmesh, mathutils
from mathutils import Vector
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
dg=bpy.context.evaluated_depsgraph_get()
def wb(n):
    o=bpy.data.objects[n]; ev=o.evaluated_get(dg); me=ev.to_mesh(); bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world); ev.to_mesh_clear(); return bm
def ovl(a,b):
    A=wb(a); B=wb(b); t=mathutils.bvhtree.BVHTree.FromBMesh(A); n=0
    for f in B.faces:
        c=f.calc_center_median(); cnt=0; o=c.copy(); d=f.normal.copy()
        for _ in range(6):
            loc,nor,idx,dist=t.ray_cast(o,d,200)
            if loc is None: break
            cnt+=1; o=loc+d*0.001
        if cnt%2==1: n+=1
    A.free(); B.free(); return n
for a,b in [('Tail','Enclosure_Lid'),('Ear_R','Enclosure_Lid'),('Ear_L','Enclosure_Lid'),
            ('Enclosure_Lid','Enclosure_Body'),('LED_Diffuser_Ring','Enclosure_Lid'),('LED_Diffuser_Ring','Enclosure_Body'),
            ('Belly_Pan','Enclosure_Body'),('Face_Plate','Enclosure_Body'),('Face_Plate','OLED_1p3_Module')]:
    print('OVL',a,'x',b,'=',ovl(a,b))
# tail base underside geometry
tail=bpy.data.objects['Tail']; mw=tail.matrix_world
vs=[mw@v.co for v in tail.data.vertices]
print('tail zmin',min(v.z for v in vs),'base x range at zmin',min(v.x for v in vs),max(v.x for v in vs))
base=[v for v in vs if v.z<64.2]
print('tail base verts',len(base),'x',round(min(v.x for v in base),2),round(max(v.x for v in base),2),'y',round(min(v.y for v in base),2),round(max(v.y for v in base),2))
