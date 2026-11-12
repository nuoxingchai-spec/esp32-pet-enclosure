import bpy
from mathutils import Vector
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob=bpy.data.objects['Enclosure_Body']
mw=ob.matrix_world
me=ob.data
# faces near the +X side around front-right leg, outward normals
print('--- +X faces x>38.5, y 20..70, z 20..60 ---')
rows=[]
for p in me.polygons:
    c=mw@p.center
    n=(mw.to_3x3()@p.normal).normalized()
    if c.x>38.5 and 20<c.y<70 and 20<c.z<60 and abs(n.x)>0.9:
        rows.append((round(c.x,3),round(c.y,2),round(c.z,2),round(n.x,2),round(p.area,1)))
for r in sorted(rows,key=lambda r:(-r[1],-r[2]))[:60]: print(r)
print('count',len(rows))
# vertical faces around the leg, any normal
print('--- surfaces between x 38.9..40.5, y 28..60, z 30..55 ---')
seen=[]
for p in me.polygons:
    c=mw@p.center
    if 38.9<c.x<40.5 and 28<c.y<60 and 30<c.z<55:
        n=(mw.to_3x3()@p.normal).normalized()
        seen.append((round(c.x,3),round(c.y,2),round(c.z,2),round(n.x,2),round(n.y,2),round(n.z,2),round(p.area,1)))
for r in sorted(seen,key=lambda r:(-r[2],r[1]))[:80]: print(r)
print('count2',len(seen))
