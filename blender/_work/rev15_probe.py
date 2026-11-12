import bpy
from mathutils import Vector
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
dg = bpy.context.evaluated_depsgraph_get()
def probe(name, org, d, dist=200):
    o=bpy.data.objects[name]; mw=o.matrix_world; inv=mw.inverted()
    ok,loc,nor,idx = o.ray_cast(inv@Vector(org), (inv.to_3x3()@Vector(d)).normalized(), distance=dist, depsgraph=dg)
    if not ok: return None
    p=mw@loc; return (round(p.x,3),round(p.y,3),round(p.z,3))
print('--- FacePlate probe -Y at holes ---')
for x in (-20.8,20.8):
    for z in (25.5,54.5):
        print(f'  x={x} z={z} hit={probe("Face_Plate",(x,80,z),(0,-1,0))}')
    for z in (30.0, 50.0):
        print(f'  x={x} z={z}(solid) hit={probe("Face_Plate",(x,80,z),(0,-1,0))}')
print('--- BellyPan probe +Z at holes ---')
for x in (-20,20):
    for y in (48,30,-50):
        print(f'  x={x} y={y} hit={probe("Belly_Pan",(x,y,5),(0,0,1))}')
    for y in (40, 0):
        print(f'  x={x} y={y}(solid) hit={probe("Belly_Pan",(x,y,5),(0,0,1))}')
print('--- Leg outer face grid scan: first hit x (leg outer=+-48) ---')
for nm,sx in [('Leg_R',1),('Leg_L',-1)]:
    print(nm)
    for z in (36,37,38,39,40):
        row=[]
        for y in (42,43,44,45,46):
            h=probe(nm,(sx*70,y,z),(-sx,0,0))
            row.append(f'{y}:{h[0] if h else None}')
        print('  z',z,' '.join(row))
