import bpy, bmesh, mathutils
from mathutils import Vector
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
dg=bpy.context.evaluated_depsgraph_get()
def wb(n):
    o=bpy.data.objects[n]; ev=o.evaluated_get(dg); me=ev.to_mesh(); bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world); ev.to_mesh_clear(); return bm
def pen(a,b):
    A=wb(a); B=wb(b); t=mathutils.bvhtree.BVHTree.FromBMesh(A); hits=[]
    for f in B.faces:
        c=f.calc_center_median(); cnt=0; o=c.copy(); d=f.normal.copy()
        for _ in range(6):
            loc,nor,idx,dist=t.ray_cast(o,d,200)
            if loc is None: break
            cnt+=1; o=loc+d*0.001
        if cnt%2==1:
            # distance to A surface both ways
            l1,n1,i1,d1=t.ray_cast(c,f.normal,50)
            l2,n2,i2,d2=t.ray_cast(c,-f.normal,50)
            hits.append((c.copy(), min(d1 if l1 else 99, d2 if l2 else 99), f.normal.copy()))
    A.free(); B.free(); return hits
for a,b in [('Enclosure_Lid','Enclosure_Body'),('Face_Plate','Enclosure_Body')]:
    h=pen(a,b)
    h.sort(key=lambda x:-x[1])
    print(a,'x',b,'n',len(h))
    for c,d,n in h[:8]:
        print(f'   at ({c.x:.2f},{c.y:.2f},{c.z:.2f}) depth~{d:.3f}')
    if h:
        import statistics
        print('   max',round(h[0][1],3),'median',round(statistics.median([x[1] for x in h]),3))
