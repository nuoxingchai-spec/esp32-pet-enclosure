import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\stage3.blend')
for name in ('Enclosure_Body','Enclosure_Lid','Face_Plate'):
    o=bpy.data.objects[name]; M=o.matrix_world
    print('==',name)
    pts=[M@v.co for v in o.data.vertices]
    sel=[p for p in pts if p.y>63.8 and 57.5<p.z<61.2 and abs(p.x)<26]
    for p in sorted(sel,key=lambda p:(-p.z,p.x)):
        if abs(p.x)<12 or abs(p.x)>17:
            print(f'  x{p.x:7.2f} y{p.y:6.2f} z{p.z:6.2f}')
    print('  count',len(sel),'zrange', (min(p.z for p in sel),max(p.z for p in sel)) if sel else None)
