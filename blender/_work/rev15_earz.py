import bpy
from mathutils import Vector
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
o=bpy.data.objects['SG90_Fit_1']; mw=o.matrix_world
vs=[mw@v.co for v in o.data.vertices]
ear=[v for v in vs if (v.y<29.0 or v.y>59.0)]
print('ear verts',len(ear),'x',min(v.x for v in ear),max(v.x for v in ear),'y',min(v.y for v in ear),max(v.y for v in ear),'z',min(v.z for v in ear),max(v.z for v in ear))
# histogram z
from collections import Counter
c=Counter(round(v.z,1) for v in ear)
print('ear z hist', sorted(c.items())[:20])
# servo body only verts within y30..58
body=[v for v in vs if 30<v.y<58]
print('body z',min(v.z for v in body),max(v.z for v in body),'x',min(v.x for v in body),max(v.x for v in body))
# body lip upside faces above ears in bay, with extents
import bmesh
b=bpy.data.objects['Enclosure_Body']; bm=bmesh.new(); bm.from_mesh(b.data); bm.transform(b.matrix_world)
for z0 in (47.55,47.9,54.0,54.35):
    fs=[f for f in bm.faces if abs(f.calc_center_median().z-z0)<0.06 and f.normal.z>-0.7 and 33<f.calc_center_median().x<37.2 and 26<f.calc_center_median().y<61]
    if fs:
        xs=[v.co.x for f in fs for v in f.verts]; ys=[v.co.y for f in fs for v in f.verts]
        print(f'body lip z~{z0}: faces {len(fs)} x[{min(xs):.2f},{max(xs):.2f}] y[{min(ys):.2f},{max(ys):.2f}]')
bm.free()
