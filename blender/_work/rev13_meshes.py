import bpy
bpy.ops.wm.open_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev13_smooth.blend")
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        print(f"OBJ {o.name:22s} data={o.data.name:22s} users={o.data.users} btn={o.data.name.startswith('Button')}")
