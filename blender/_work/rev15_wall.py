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
print('body inner wall -X at rear: ray from x=-20 outward -X')
for z in (57.0,58.0,58.5,58.8,59.0,59.2,59.4,59.6,59.8):
    for y in (-40,-45,0,40):
        print(f'  z{z} y{y} -> {hit("Enclosure_Body",(-20,y,z),(-1,0,0))}')
    print()
print('lid lip outer -X: ray from x=-20 outward -X')
for z in (58.9,59.2,59.5,60.0,60.4):
    print(f'  z{z} -> {hit("Enclosure_Lid",(-20,-40,z),(-1,0,0))} / {hit("Enclosure_Lid",(-20,40,z),(-1,0,0))}')
print('lid outer -X: ray inward +X from x=-50')
for z in (59.0,59.5,60.0,60.5,61.0):
    print(f'  z{z} -> {hit("Enclosure_Lid",(-50,-40,z),(1,0,0))}')
