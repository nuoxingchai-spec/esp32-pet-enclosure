import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend")
o=bpy.data.objects['SG90_Fit_1']; mw=o.matrix_world
pts=[mw@v.co for v in o.data.vertices]
print('verts',len(pts),'bbox',tuple(round(min(p[i] for p in pts),2) for i in range(3)),tuple(round(max(p[i] for p in pts),2) for i in range(3)))
for zc,yc in ((38,44),(35,44),(40,44),(33,44),(38,50),(38,35)):
    sel=[p for p in pts if abs(p.z-zc)<2 and abs(p.y-yc)<4]
    if sel:
        print(f'z={zc} y={yc}: n={len(sel)} x[{min(p.x for p in sel):.2f},{max(p.x for p in sel):.2f}] '
              f'y[{min(p.y for p in sel):.2f},{max(p.y for p in sel):.2f}] z[{min(p.z for p in sel):.2f},{max(p.z for p in sel):.2f}]')
# slab z 30-44, y 30-58: x histogram
sel=[p for p in pts if 30<p.z<44 and 30<p.y<58]
import collections
h=collections.Counter(round(p.x,1) for p in sel)
print('x hist', sorted(h.items()))
# faces near x=14-20
print('faces x centers < 22:')
fs=[o.data.polygons[i] for i in range(len(o.data.polygons)) if (mw@o.data.polygons[i].center).x<22]
print(len(fs), [(round((mw@f.center).x,1),round((mw@f.center).y,1),round((mw@f.center).z,1),round(f.area,2)) for f in fs[:20]])
