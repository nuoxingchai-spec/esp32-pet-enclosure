import bpy, bmesh, math
from mathutils import Vector
F=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob=bpy.data.objects['Enclosure_Body']
me=ob.data
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
print('verts',len(bm.verts),'edges',len(bm.edges),'faces',len(bm.faces))
# connected components
seen=set(); comps=[]
for v in bm.verts:
    if v.index in seen: continue
    stack=[v]; seen.add(v.index); n=0; zmin=1e9; zmax=-1e9
    while stack:
        x=stack.pop(); n+=1; zmin=min(zmin,x.co.z); zmax=max(zmax,x.co.z)
        for e in x.link_edges:
            o=e.other_vert(x)
            if o.index not in seen:
                seen.add(o.index); stack.append(o)
    comps.append((n,round(zmin,2),round(zmax,2)))
print('components',len(comps),sorted(comps,reverse=True)[:10])
# edges near seam z=54.35
seam=[]
for e in bm.edges:
    a,b=e.verts
    if abs(a.co.z-54.35)<0.02 and abs(b.co.z-54.35)<0.02:
        seam.append(e)
print('seam edges',len(seam))
if seam:
    lens=[e.calc_length() for e in seam]
    print('  len min/max',round(min(lens),3),round(max(lens),3))
    # normals of adjacent faces
    diffs=[]
    for e in seam:
        fs=e.link_faces
        if len(fs)==2:
            diffs.append(math.degrees(fs[0].normal.angle(fs[1].normal)))
    if diffs:
        print('  adjacent normal angle min/avg/max',round(min(diffs),2),round(sum(diffs)/len(diffs),2),round(max(diffs),2))
    # duplicate verts at seam
    vs=[e.verts[0] for e in seam]+[e.verts[1] for e in seam]
    uniq=set(v.index for v in vs)
    print('  unique verts touching seam',len(uniq))
    # cluster duplicates by position
    from collections import defaultdict
    pos=defaultdict(list)
    for i in uniq:
        v=bm.verts[i]; pos[(round(v.co.x,3),round(v.co.y,3),round(v.co.z,3))].append(i)
    dups={k:v for k,v in pos.items() if len(v)>1}
    print('  duplicate positions',len(dups), 'max stack', max((len(v) for v in dups.values()), default=0))
# corner region faces z45..58, x>38, y<-55
print('corner faces:')
cnt=0
for f in bm.faces:
    c=f.calc_center_median()
    if c.x>38.2 and c.y<-55.5 and 45<c.z<58:
        cnt+=1
print('  count',cnt)
# z-level histogram of verts in corner region
from collections import Counter
h=Counter()
for v in bm.verts:
    if v.co.x>38.0 and v.co.y<-55.0 and 20<v.co.z<60:
        h[round(v.co.z,2)]+=1
print('  corner verts z histogram (top 25):',h.most_common(25))
# edge lengths and face sizes near seam corner
fs=[f for f in bm.faces if f.calc_center_median().x>38.2 and f.calc_center_median().y<-55.5 and 45<f.calc_center_median().z<58]
zs=Counter()
for f in fs:
    zs[round(max(v.co.z for v in f.verts),2)]+=1
print('  corner faces max-z histogram:',zs.most_common(12))
print('  smooth faces',sum(1 for f in bm.faces if f.smooth),'/',len(bm.faces))
bm.free()
