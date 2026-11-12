import bpy
from mathutils import Vector
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
dg=bpy.context.evaluated_depsgraph_get()
def hit(name,org,d,dist=200):
    o=bpy.data.objects[name]; ev=o.evaluated_get(dg); mw=o.matrix_world; inv=mw.inverted()
    ok,loc,nor,idx=ev.ray_cast(inv@Vector(org),(inv.to_3x3()@Vector(d)).normalized(),distance=dist)
    if not ok: return None
    p=mw@loc; return (round(p.x,3),round(p.y,3),round(p.z,3))
for z in (58.7,58.8,58.9,59.0,59.1,59.2,59.3,59.35,59.4):
    vals=[]
    for y in (-55,-50,-45,-40,-35,-30):
        h=hit('Enclosure_Body',(-20,y,z),(-1,0,0))
        vals.append(f'{y}:{h[0] if h else None}')
    print(f'z{z}', ' '.join(vals))
print('right side +X:')
for z in (58.8,59.0,59.2,59.4):
    vals=[]
    for y in (-55,-50,-45,-40,-35,-30):
        h=hit('Enclosure_Body',(20,y,z),(1,0,0))
        vals.append(f'{y}:{h[0] if h else None}')
    print(f'z{z}', ' '.join(vals))
