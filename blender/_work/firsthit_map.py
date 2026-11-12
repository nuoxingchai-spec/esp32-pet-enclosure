import bpy
from mathutils import Vector
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
dg=bpy.context.evaluated_depsgraph_get()
skip={'Cube','Preview_Ground','Button_Top_Master','Ear_R_Master','Ear_L_Master','Tail_Master','Pet_Body_Blockout','V1_Base','V1_Lid'}
objs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in skip]
for o in objs:
    m=o.active_material
    print(f"{o.name:20s} mat={m.name if m else '-':18s} col={tuple(round(c,2) for c in m.diffuse_color[:3]) if m else '-'}")

def first(side,y,z):
    best=None
    for o in objs:
        mw=o.matrix_world; mi=mw.inverted()
        org=mi@Vector((60.0*side,y,z))
        d=(mw.to_3x3().inverted()@Vector((-side,0,0))).normalized()
        ok,loc,nor,idx=o.ray_cast(org,d,distance=200.0,depsgraph=dg)
        if ok:
            w=mw@loc; dist=(Vector((60.0*side,y,z))-w).length
            if best is None or dist<best[0]:
                best=(dist,o.name,w)
    return best

names=[o.name for o in objs]
chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij'
uniq={}
for n in names:
    if n not in uniq: uniq[n]=chars[len(uniq)]
print('LEGEND:', ' '.join(f'{uniq[n]}={n}' for n in names))
for side in (1,-1):
    print('='*80)
    print(('RIGHT +X' if side>0 else 'LEFT -X')+' first hit, y -64..64 step1, z 58..20 step1')
    for z in range(58,19,-1):
        row=[]
        for y in range(-64,65):
            b=first(side,y,z)
            row.append('.' if b is None else uniq[b[1]])
        print(f'z{z:3d} '+''.join(row))
