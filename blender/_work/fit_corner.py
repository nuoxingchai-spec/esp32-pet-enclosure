import bpy
from mathutils import Vector
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
for n in ['SG90_Fit_2','SG90_Fit_4','SG90_Fit_1']:
    o=bpy.data.objects[n]
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    tail=[v for v in vs if abs(v.y)>58]
    print(n,'all y',round(min(abs(v.y) for v in vs),1),round(max(abs(v.y) for v in vs),1),
          'nearCorner',len(tail))
    if tail:
        print('  x',round(min(v.x for v in tail),1),round(max(v.x for v in tail),1),
              'z',round(min(v.z for v in tail),1),round(max(v.z for v in tail),1))
    # vertices inboard of body wall at rear
    inb=[v for v in vs if abs(v.y)>57 and 30<abs(v.x)<38.5 and v.z<54]
    print('  inboard rear verts',len(inb), (round(min(v.z for v in inb),1),round(max(v.z for v in inb),1)) if inb else '')
