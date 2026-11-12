import bpy
from mathutils import Vector
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
o = bpy.data.objects['SG90_Fit_1']
vs = [o.matrix_world @ v.co for v in o.data.vertices]
def rng(sel, axis):
    vals=[getattr(p,axis) for p in sel]
    return (round(min(vals),2), round(max(vals),2)) if vals else None
for name, sel in [
  ("x<16", [p for p in vs if p.x<16]),
  ("16<=x<20", [p for p in vs if 16<=p.x<20]),
  ("20<=x<26", [p for p in vs if 20<=p.x<26]),
  ("26<=x<36.6", [p for p in vs if 26<=p.x<36.6]),
  ("x>=36.6", [p for p in vs if p.x>=36.6]),
  ("y<32.6", [p for p in vs if p.y<32.6]),
  ("y>55.4", [p for p in vs if p.y>55.4]),
  ("z<31.9", [p for p in vs if p.z<31.9]),
  ("z>44.1", [p for p in vs if p.z>44.1]),
]:
    print(f"{name:12s} n={len(sel):4d} x={rng(sel,'x')} y={rng(sel,'y')} z={rng(sel,'z')}")
