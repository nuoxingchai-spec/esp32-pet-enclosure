import bpy
from mathutils import Vector
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob=bpy.data.objects['Enclosure_Body']; mw=ob.matrix_world; mi=mw.inverted()
dg=bpy.context.evaluated_depsgraph_get()
def hx(side,y,z):
    org=mi@Vector((60.0*side,y,z)); d=(mw.to_3x3().inverted()@Vector((-side,0,0))).normalized()
    ok,loc,nor,idx=ob.ray_cast(org,d,distance=200.0,depsgraph=dg)
    return None if not ok else (mw@loc).x
for side in (1,-1):
    for ya in (-1,1):
        best=(0,None)
        y=55.0
        while y<=63.0:
            lo=hx(side,ya*y,52.0); up=hx(side,ya*y,56.0)
            if lo and up:
                d=abs(lo)-abs(up)
                if d>best[0]: best=(d,y)
            y+=0.1
        print(f'side={side:+d} end={"rear" if ya<0 else "front"} max step={best[0]:.2f} at |y|={best[1]:.1f}')
        # also step at y=60, 61, 62
        print('   ', [(round(ya*t,1), round(abs(hx(side,ya*t,52.0))-abs(hx(side,ya*t,56.0)),2)) for t in (58,59,60,61,62,63)])
