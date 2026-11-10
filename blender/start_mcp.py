import bpy
import addon_utils
import traceback

try:
    addon_utils.enable("blender_mcp", default_set=True)
    result = bpy.ops.blendermcp.start_server()
    scene = bpy.context.scene
    print(
        "BlenderMCP start:",
        result,
        "running:",
        getattr(scene, "blendermcp_server_running", None),
        "port:",
        getattr(scene, "blendermcp_port", None),
    )
except Exception:
    traceback.print_exc()
