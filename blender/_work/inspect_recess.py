import bpy
from mathutils import Vector
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob=bpy.data.objects['Enclosure_Body']; me=ob.data; mw=ob.matrix_world
rows=[]
for p in me.polygons:
    c=mw@p.center; n=(mw.to_3x3()@p.normal).normalized()
    if 36.5<c.x<39.0 and 25<c.y<64 and 20<c.z<60 and n.x>0.85 and p.area>2:
        rows.append((round(c.x,3),round(c.y,2),round(c.z,2),round(n.x,2),round(p.area,1)))
print('large +X faces x36.5-39 near front-right:')
for r in sorted(rows,key=lambda r:(r[0],-r[4]))[:30]: print(r)
print('count',len(rows))
# outline of recess floor x<38.8: extents
xs=[];ys=[];zs=[]
for p in me.polygons:
    c=mw@p.center; n=(mw.to_3x3()@p.normal).normalized()
    if 36.5<c.x<38.8 and 25<c.y<64 and 20<c.z<60 and n.x>0.85:
        xs.append(c.x);ys.append(c.y);zs.append(c.z)
print('floor x', round(min(xs),3), round(max(xs),3), 'y', round(min(ys),2), round(max(ys),2), 'z', round(min(zs),2), round(max(zs),2), 'faces',len(xs))
# vertices of recess floor near its border -> get exact bounds
vs=[]
for v in me.vertices:
    co=mw@v.co
    if 36.5<co.x<38.8 and 25<co.y<64 and 20<co.z<60:
        vs.append(co)
print('verts',len(vs))
if vs:
    print('vx',round(min(v.x for v in vs),3),round(max(v.x for v in vs),3),'vy',round(min(v.y for v in vs),2),round(max(v.y for v in vs),2),'vz',round(min(v.z for v in vs),2),round(max(v.z for v in vs),2))
