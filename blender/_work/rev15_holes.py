import bpy
from mathutils import Vector
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)

def clusters(points, tol=0.6):
    pts = sorted(points)
    out=[]
    for p in pts:
        for c in out:
            if abs(p[0]-c[0][0])<tol and abs(p[1]-c[0][1])<tol:
                c.append(p); break
        else: out.append([p])
    return sorted((sum(x for x,y in c)/len(c), sum(y for x,y in c)/len(c), len(c)) for c in out)

for nm, axis, sign in [('Leg_L','X',-1), ('Leg_R','X',1)]:
    o=bpy.data.objects[nm]; mw=o.matrix_world
    vs=[mw@v.co for v in o.data.vertices]
    xo = min(v.x for v in vs) if sign<0 else max(v.x for v in vs)
    face=[(v.y,v.z) for v in vs if abs(v.x-xo)<0.01]
    print(nm, 'outer x', round(xo,3), 'verts', len(face))
    for c in clusters(face):
        if c[2]>=8: print('   hole?', [round(x,2) for x in c])
# servo horn holes at outer x plane
for nm, xo in [('SG90_Fit_1',42.7),('SG90_Fit_2',42.7),('SG90_Fit_3',-42.7),('SG90_Fit_4',-42.7)]:
    o=bpy.data.objects[nm]; mw=o.matrix_world
    vs=[mw@v.co for v in o.data.vertices]
    face=[(v.y,v.z) for v in vs if abs(v.x-xo)<0.05]
    print(nm,'x',xo,'verts',len(face))
    for c in clusters(face):
        if c[2]>=6: print('   circ?', [round(x,2) for x in c])
# Face plate hole rims: front face y max
fp=bpy.data.objects['Face_Plate']; mw=fp.matrix_world
vs=[mw@v.co for v in fp.data.vertices]
yo=max(v.y for v in vs)
face=[(v.x,v.z) for v in vs if abs(v.y-yo)<0.01]
print('FacePlate front y',round(yo,2),'verts',len(face))
for c in clusters(face):
    if c[2]>=8: print('   hole?', [round(x,2) for x in c])
# Belly pan bottom face z min
bp=bpy.data.objects['Belly_Pan']; mw=bp.matrix_world
vs=[mw@v.co for v in bp.data.vertices]
zo=min(v.z for v in vs)
face=[(v.x,v.y) for v in vs if abs(v.z-zo)<0.01]
print('BellyPan bottom z',round(zo,2),'verts',len(face))
for c in clusters(face):
    if c[2]>=8: print('   hole?', [round(x,2) for x in c])
