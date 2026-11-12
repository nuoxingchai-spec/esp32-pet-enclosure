import bpy, bmesh
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
for nm in ['Enclosure_Lid','Enclosure_Body']:
    o=bpy.data.objects[nm]
    print(nm,'loc',tuple(round(x,2) for x in o.location),'mods',[m.type for m in o.modifiers])
    zs=[v.co.z for v in o.data.vertices]
    print('  local z',round(min(zs),2),round(max(zs),2),'world z',round(min(zs)+o.location.z,2),round(max(zs)+o.location.z,2),
          'verts',len(o.data.vertices),'polys',len(o.data.polygons))
    bm=bmesh.new(); bm.from_mesh(o.data)
    # components
    seen=set(); comps=[]
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        if v.index in seen: continue
        stack=[v]; cnt=0; zmin=999; zmax=-999
        while stack:
            x=stack.pop()
            if x.index in seen: continue
            seen.add(x.index); cnt+=1; zmin=min(zmin,x.co.z); zmax=max(zmax,x.co.z)
            for e in x.link_edges:
                ov=e.other_vert(x)
                if ov.index not in seen: stack.append(ov)
        comps.append((cnt,round(zmin,2),round(zmax,2)))
    comps.sort(reverse=True)
    print('  comps',len(comps),comps[:8])
    bm.free()
