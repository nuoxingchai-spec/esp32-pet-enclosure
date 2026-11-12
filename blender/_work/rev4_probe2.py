import bpy, bmesh, math
from mathutils import Vector

F = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
ob = bpy.data.objects['Enclosure_Body']
mw = ob.matrix_world
mi = mw.inverted()
dg = bpy.context.evaluated_depsgraph_get()
M3 = mw.to_3x3(); M3i = M3.inverted()

def ray_out(sx, sy, cx, cy, z, th_deg, back=60.0):
    th = math.radians(th_deg)
    ux, uy = sx * math.cos(th), sy * math.sin(th)
    org = mi @ Vector((cx + back * ux, cy + back * uy, z))
    d = (M3i @ Vector((-ux, -uy, 0.0))).normalized()
    ok, loc, nor, idx = ob.ray_cast(org, d, distance=300.0, depsgraph=dg)
    if not ok: return None
    p = mw @ loc
    return math.hypot(p.x - cx, p.y - cy)

print("=== RR corner r(theta): z sweep (C=30,-55) ===")
hdr = [0,10,20,25,30,33,35,37,40,45,50,60,70,80,90]
print("z     " + " ".join(f" th{t:<3d}" for t in hdr))
for z in [24,30,36,40,44,46,48,49,50,51,52,53,54,54.34,54.36,54.5,55,56,57,58,59]:
    row = []
    for th in hdr:
        r = ray_out(1,-1,30.0,-55.0,z,th)
        row.append("  --  " if r is None else f"{r:6.3f}")
    print(f"z{z:5.2f}" + " ".join(row))

print("\n=== vertical rays: material/cavity at corner (world z) ===")
for (x,y) in [(30,-55),(34,-58),(37,-60),(38.5,-60.8),(36.6,-61.6),(32,-62),(30,-62.5),(34,-62),(38,-62),(38.5,-59),(37.5,-59.5)]:
    org = mi @ Vector((x,y,19.0))
    d = (M3i @ Vector((0,0,1))).normalized()
    hits = []
    z = 19.0; guard = 0
    # march: repeated ray casts upward
    o = Vector((x,y,19.0))
    while guard < 30:
        ok, loc, nor, idx = ob.ray_cast(mi @ o, (M3i @ Vector((0,0,1))).normalized(), distance=200.0, depsgraph=dg)
        if not ok: break
        p = mw @ loc
        hits.append(round(p.z,3))
        o = Vector((p.x, p.y, p.z + 0.001)); guard += 1
    print(f"({x:5.1f},{y:6.1f}) up hits {hits}")

print("\n=== z54.35 loops, proper classification ===")
bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(mw)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table(); bm.edges.ensure_lookup_table()
def is_sliver(f):
    zs=[v.co.z for v in f.verts]
    return min(zs)>54.30 and max(zs)<54.40 and f.normal.z>0.9
zr = [v for v in bm.verts if abs(v.co.z-54.35)<0.02]
lo=set(); up=set(); amb=set()
for v in zr:
    below=any((not is_sliver(f)) and min(x.co.z for x in f.verts)<54.30 for f in v.link_faces)
    above=any((not is_sliver(f)) and max(x.co.z for x in f.verts)>54.40 for f in v.link_faces)
    if below and not above: lo.add(v.index)
    elif above and not below: up.add(v.index)
    else: amb.add(v.index)
print('verts',len(zr),'LO',len(lo),'UP',len(up),'amb',len(amb))
for lab,s in (('LO',lo),('UP',up),('AMB',amb)):
    pts=[bm.verts[i].co for i in s]
    if pts:
        print(lab,'x',round(min(p.x for p in pts),3),round(max(p.x for p in pts),3),
              'y',round(min(p.y for p in pts),3),round(max(p.y for p in pts),3))

def loop_order(idx):
    vs={i:bm.verts[i] for i in idx}
    nb={i:[] for i in idx}
    for e in bm.edges:
        a,b=e.verts[0].index,e.verts[1].index
        if a in vs and b in vs:
            nb[a].append(b); nb[b].append(a)
    start=next(i for i in idx if len(nb[i])>0)
    order=[start]; prev=None; cur=start
    while True:
        nxt=[n for n in nb[cur] if n!=prev]
        if not nxt: break
        prev,cur=cur,nxt[0]
        if cur==start: break
        order.append(cur)
    return order
for lab,s in (('LO',lo),('UP',up)):
    if not s: continue
    o=loop_order(s)
    print(lab,'ordered',len(o),'closed' if o[0]==o[-1] else 'open', 'deg1', sum(1 for i in s if len([e for e in bm.verts[i].link_edges if e.other_vert(bm.verts[i]).index in s])==1))
    # print right-side rear points
    pts=[bm.verts[i].co for i in o]
    sr=[p for p in pts if p.x>0 and p.y<0]
    print(lab,'RR count',len(sr))
    for p in sorted(sr,key=lambda p:-p.y)[:20]:
        print('  ',lab,tuple(round(v,3) for v in p))

print("\n=== rim sliver faces count by region ===")
cnt=0; verts_in=0
for f in bm.faces:
    if is_sliver(f):
        c=f.calc_center_median()
        if abs(c.x)>38.5 or abs(c.y)>63.5: cnt+=1
print('outer sliver faces',cnt)
bm.free()
print('DONE')
