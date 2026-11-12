import bpy
from mathutils import Vector
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
for on in ['SG90_Fit_1','Leg_R']:
    o=bpy.data.objects[on]; mw=o.matrix_world
    vs=[mw@v.co for v in o.data.vertices]
    print(on,'bbox',[(round(min(v[i] for v in vs),2),round(max(v[i] for v in vs),2)) for i in range(3)])
    if on=='SG90_Fit_1':
        for xmin in (36.0,38.0,39.0,40.0,41.0):
            sub=[v for v in vs if v.x>xmin]
            if sub:
                print('  x>',xmin,'n',len(sub),'y',round(min(v.y for v in sub),2),round(max(v.y for v in sub),2),'z',round(min(v.z for v in sub),2),round(max(v.z for v in sub),2))
    else:
        # inner face x near 40..43, find slot void vertices / extents
        sub=[v for v in vs if v.x<40.2]
        print('  x<40.2 n',len(sub),'y',round(min(v.y for v in sub),2),round(max(v.y for v in sub),2),'z',round(min(v.z for v in sub),2),round(max(v.z for v in sub),2))
        for xr in [(40.0,41.0),(41.0,42.0),(42.0,43.0),(43.0,44.0)]:
            sub=[v for v in vs if xr[0]<=v.x<xr[1] and 30<v.y<58]
            if sub:
                print('  x',xr,'n',len(sub),'y',round(min(v.y for v in sub),2),round(max(v.y for v in sub),2),'z',round(min(v.z for v in sub),2),round(max(v.z for v in sub),2))
