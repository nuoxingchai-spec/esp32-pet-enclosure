import bpy, bmesh, math
from mathutils import Vector
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
def bb(n):
    o=bpy.data.objects[n]; xs=[];ys=[];zs=[]
    for c in o.bound_box:
        p=o.matrix_world@Vector(c); xs.append(p.x);ys.append(p.y);zs.append(p.z)
    print(f"{n:18s} x[{min(xs):.2f},{max(xs):.2f}] y[{min(ys):.2f},{max(ys):.2f}] z[{min(zs):.2f},{max(zs):.2f}]")
for n in ['Leg_L','Leg_R','Leg_L_Rear','Leg_R_Rear','SG90_Fit_1','SG90_Fit_2','SG90_Fit_3','SG90_Fit_4',
          'PCB_Board','PCB_Components','Battery_103450','Speaker_3070','OLED_1p3_Module']:
    bb(n)
# leg screw hole anchors: find circular hole in leg near x axis
leg = bpy.data.objects['Leg_L']; mw=leg.matrix_world
# gather vertices near x max side (outer face) and z near 38
vs = [mw@v.co for v in leg.data.vertices]
print('LEG_L xmax', max(v.x for v in vs), 'xmin', min(v.x for v in vs))
# Tail overhang analysis in print orientation (master, z-up)
tail = bpy.data.objects['Tail_Master']
bm = bmesh.new(); bm.from_mesh(tail.data)
bm.transform(tail.matrix_world)
area_down = sum(f.calc_area() for f in bm.faces if f.normal.z < -0.5)
area_all = sum(f.calc_area() for f in bm.faces)
zmin = min(v.co.z for v in bm.verts); zmax = max(v.co.z for v in bm.verts)
print(f"TAIL overhang(down) {area_down:.1f} of {area_all:.1f} mm2  z[{zmin:.2f},{zmax:.2f}]")
# bucket down-facing area by z
buckets={}
for f in bm.faces:
    if f.normal.z < -0.5:
        z = f.calc_center_median().z
        k = round(z//5*5)
        buckets[k]=buckets.get(k,0)+f.calc_area()
print('TAIL down-area by z:', {k:round(v,1) for k,v in sorted(buckets.items())})
bm.free()
# Ear overhang
for nm in ['Ear_R_Master','Tail_Master']:
    o=bpy.data.objects[nm]; bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    da=sum(f.calc_area() for f in bm.faces if f.normal.z<-0.5); aa=sum(f.calc_area() for f in bm.faces)
    print(f"{nm} down={da:.1f}/{aa:.1f} ({da/aa*100:.1f}%)")
    bm.free()
