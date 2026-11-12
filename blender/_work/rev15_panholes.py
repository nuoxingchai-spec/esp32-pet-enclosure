import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend')
dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['Belly_Pan']; ev=o.evaluated_get(dg); mw=o.matrix_world; inv=mw.inverted()
print('pan loc', tuple(round(v,2) for v in o.location), 'bbox z', min(v.co.z for v in o.data.vertices), max(v.co.z for v in o.data.vertices))
for r in [0.8,1.2,1.6,2.0,2.4,2.8,3.2]:
    # from below at (20+r,48), ray +Z
    ok,loc,nor,idx=ev.ray_cast(inv@Vector((20+r,48,10)),(inv.to_3x3()@Vector((0,0,1))).normalized(),distance=100)
    z1=(mw@loc).z if ok else None
    ok,loc,nor,idx=ev.ray_cast(inv@Vector((20+r,48,30)),(inv.to_3x3()@Vector((0,0,-1))).normalized(),distance=100)
    z2=(mw@loc).z if ok else None
    print(f'r={r}  first-from-below z={z1 if z1 is None else round(z1,3)}  first-from-above z={z2 if z2 is None else round(z2,3)}')
# faceplate hole profile at (20.8, 64.05, 25.5), from front +Y looking -Y
fp=bpy.data.objects['Face_Plate']; ef=fp.evaluated_get(dg); mwf=fp.matrix_world; invf=mwf.inverted()
print('faceplate loc', tuple(round(v,2) for v in fp.location))
for r in [0.8,1.2,1.6,2.0,2.4]:
    ok,loc,nor,idx=ef.ray_cast(invf@Vector((20.8+r,70,25.5)),(invf.to_3x3()@Vector((0,-1,0))).normalized(),distance=100)
    y=(mwf@loc).y if ok else None
    print(f'face r={r} first from +Y y={y if y is None else round(y,3)}')
