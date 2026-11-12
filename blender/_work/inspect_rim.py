import bpy, bmesh
from collections import Counter, defaultdict
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob=bpy.data.objects['Enclosure_Body']; mw=ob.matrix_world
bm=bmesh.new(); bm.from_mesh(ob.data); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
def w(v): return mw @ v.co
def wp(p): return mw @ p
# horizontal +Z faces at z=54.35 on the outer perimeter
rim=[]
for f in bm.faces:
    zs=[w(v).z for v in f.verts]
    if min(zs)>54.30 and max(zs)<54.40 and f.normal.z>0.9:
        c=wp(f.calc_center_median())
        if abs(c.x)>38.5 or abs(c.y)>63.5:
            rim.append(f)
print('outer rim faces',len(rim))
areas=[f.calc_area() for f in rim]
print('area min/median/max',round(min(areas),4),round(sorted(areas)[len(areas)//2],4),round(max(areas),3))
# classify by side and extent
for f in rim[:12]:
    vs=[w(v) for v in f.verts]
    print(' f',f.index,'area',round(f.calc_area(),4),'n',tuple(round(x,2) for x in f.normal),
          'xy',[(round(v.x,3),round(v.y,3)) for v in vs])
# group rim faces by y sign / x near 39
groups=defaultdict(int)
for f in rim:
    c=wp(f.calc_center_median())
    if abs(c.x)>38.5 and abs(c.y)<56: key=('side', 'R' if c.x>0 else 'L')
    elif abs(c.y)>63.5 and abs(c.x)<32: key=('end','front' if c.y>0 else 'rear')
    else: key=('corner', f'{c.x:+.0f},{c.y:+.0f}')
    groups[key]+=1
print('groups',dict(groups))
# side R rim: widths in x, y positions
sideR=[f for f in rim if abs(w(f.calc_center_median()).x)>38.5 and abs(w(f.calc_center_median()).y)<56]
print('sideR count',len(sideR))
for f in sideR[:6]+sideR[-3:]:
    vs=[w(v) for v in f.verts]; xs=[round(v.x,3) for v in vs]; ys=[round(v.y,2) for v in vs]
    print('  ',f.index,'x',xs,'y',ys,'area',round(f.calc_area(),4))
# all z levels of the rim faces
print('rim z uniq',Counter(round(w(v).z,2) for f in rim for v in f.verts).most_common(6))
bm.free()
