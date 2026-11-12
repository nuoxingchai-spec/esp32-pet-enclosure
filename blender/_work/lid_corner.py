import bpy
from mathutils import Vector
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
dg=bpy.context.evaluated_depsgraph_get()
def hx(name,side,y,z):
    ob=bpy.data.objects[name]; mw=ob.matrix_world; mi=mw.inverted()
    org=mi@Vector((60.0*side,y,z)); d=(mw.to_3x3().inverted()@Vector((-side,0,0))).normalized()
    ok,loc,nor,idx=ob.ray_cast(org,d,distance=200.0,depsgraph=dg)
    return None if not ok else round((mw@loc).x,2)
for name in ('Enclosure_Lid','Enclosure_Body'):
    print('==',name)
    for z in ([58.9,59.2,59.8,60.5,61.5,63,65,66.5] if name=='Enclosure_Lid' else [52,54,56,58.5,59.5]):
        vals=[]
        for y in (-62,-61,-60,-59,-58,-56,-50,50,56,58,59,60,61,62):
            vals.append((y,hx(name,1,y,z)))
        print(' z',z,vals)
