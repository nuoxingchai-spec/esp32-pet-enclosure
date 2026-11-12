import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
body = bpy.data.objects['Enclosure_Body']
bm = bmesh.new(); bm.from_mesh(body.data); bm.transform(body.matrix_world); tb=BVHTree.FromBMesh(bm); bm.free()
bm3=bmesh.new(); bmesh.ops.create_cube(bm3,size=1.0)
for v in bm3.verts:
    v.co.x=14.3+(v.co.x+0.5)*(36.4-14.3)
    v.co.y=32.8+(v.co.y+0.5)*(55.2-32.8)
    v.co.z=32.1+(v.co.z+0.5)*(43.9-32.1)
bm3.faces.ensure_lookup_table()
t3=BVHTree.FromBMesh(bm3); 
pairs=tb.overlap(t3)
print("pairs", len(pairs))
cent=[]
for i,j in pairs:
    c=sum((bm3.faces[j].calc_center_median(),), Vector())
    cent.append(c)
xs=[c.x for c in cent]; ys=[c.y for c in cent]; zs=[c.z for c in cent]
print("box face centroids x", (round(min(xs),2),round(max(xs),2)), "y",(round(min(ys),2),round(max(ys),2)), "z",(round(min(zs),2),round(max(zs),2)))
from collections import Counter
cz=Counter(round(c.z,1) for c in cent)
print("z hist", sorted(cz.items())[:20])
bm3.free()
# body material map around the bay floor after cut
bm = bmesh.new(); bm.from_mesh(body.data); bm.transform(body.matrix_world); tb=BVHTree.FromBMesh(bm); bm.free()
def mat(x,y,z):
    o=Vector((-200,y,z)); dv=Vector((1,0,0)); n=0; last=-1e9; g=0
    while g<300:
        g+=1
        loc,nor,idx,dist=tb.ray_cast(o,dv,1000.0)
        if loc is None or loc.x>x: break
        if loc.x-last>0.2: n+=1; last=loc.x
        o=loc+dv*0.1
    return n%2==1
for x in (26.5,28,30,32,34,36,36.4):
    col=""
    for i in range(300,350):
        z=i/10
        col += "M" if mat(x,44,z) else "."
    print(f"x={x:5.1f} z30.0-35.0: {col}")
for x in (26.5,32,36,36.4):
    print(f"x={x}:")
    for y in (28,30,32,34,44,54,56,58,60):
        col=""
        for i in range(310,341):
            z=i/10
            col += "M" if mat(x,y,z) else "."
        print(f"   y={y:5.1f} z31.0-34.0: {col}")
