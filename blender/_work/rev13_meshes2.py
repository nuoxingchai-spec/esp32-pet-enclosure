import bpy
bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend")
for n in ('Enclosure_Lid','Button_Top_1','Button_Top_Master'):
    o = bpy.data.objects[n]
    print(f"OBJ {o.name:18s} data={o.data.name:22s} users={o.data.users} verts={len(o.data.vertices)}")
print('MESH DATABLOCKS:', [m.name for m in bpy.data.meshes if 'Lid' in m.name or 'Button' in m.name])
