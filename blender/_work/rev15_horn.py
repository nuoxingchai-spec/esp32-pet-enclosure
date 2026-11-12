import bpy
from mathutils import Vector
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
dg=bpy.context.evaluated_depsgraph_get()
def hits(name,org,d,dist=100):
    o=bpy.data.objects[name]; mw=o.matrix_world; inv=mw.inverted()
    o2=o.evaluated_get(dg)
    ok,loc,nor,idx=o2.ray_cast(inv@Vector(org),(inv.to_3x3()@Vector(d)).normalized(),distance=dist)
    p=mw@loc if ok else None
    return None if not ok else (round(p.x,2),round(p.y,2),round(p.z,2))
for nm,sx in [('SG90_Fit_1',1),('SG90_Fit_3',-1)]:
    print(nm)
    for y in (44,):
        for z in (38,39,40):
            print('  pivot',y,z,'-X hit',hits(nm,(sx*70,y,z),(-sx,0,0)))
    # scan horn face for hole
    for z in (36,37,38,39,40,41):
        row=[]
        for y in (42,43,44,45,46):
            h=hits(nm,(sx*70,y,z),(-sx,0,0))
            row.append(f'{y}:{h[0] if h else None}')
        print('  z',z,' '.join(row))
# leg hole through path: ray from x+70 at pivot and list if it traverses
for nm,sx in [('Leg_R',1),('Leg_L',-1)]:
    print(nm,'through pivot',hits(nm,(sx*70,44,38),(-sx,0,0)))
