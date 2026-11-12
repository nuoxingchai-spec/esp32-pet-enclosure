import bpy, bmesh, math, os
from mathutils import Vector
ROOT=r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=os.path.join(ROOT,'stl','v3','Enclosure_Lid.stl'), global_scale=1.0)
o=bpy.context.selected_objects[0]; bm=bmesh.new(); bm.from_mesh(o.data); bm.normal_update()
for lab,Bv in [('top-down B=-Z',(0,0,-1)),('underside-down B=+Z',(0,0,1))]:
    B=Vector(Bv); mn=min(f.calc_center_median().dot(B) for f in bm.faces); over=0; contact=0
    for f in bm.faces:
        d=f.normal.dot(B); c=f.calc_center_median(); a=f.calc_area()
        if c.dot(B)<mn+0.25:
            if d<-0.9: contact+=a
            continue
        if d<-0.02:
            ang=math.degrees(math.acos(max(-1,min(1,d))))-90
            if ang>45: over+=a
    print(lab,'contact',round(contact,1),'over45',round(over,1))
bm.free()
