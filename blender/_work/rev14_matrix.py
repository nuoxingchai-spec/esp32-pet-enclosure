import bpy
from mathutils.bvhtree import BVHTree
BLEND = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)

def bvh(o):
    m = o.matrix_world
    vs = [m @ v.co for v in o.data.vertices]
    fs = [tuple(p.vertices) for p in o.data.polygons]
    return BVHTree.FromPolygons(vs, fs, all_triangles=False)

names = ['OLED_1p3_Module','OLED_ActiveArea','PCB_Board','PCB_Components','Battery_103450','Speaker_3070',
         'SG90_Fit_1','SG90_Fit_2','SG90_Fit_3','SG90_Fit_4','Touch_Module_Fit',
         'Enclosure_Body','Enclosure_Lid','Enclosure_Body','Face_Plate','Belly_Pan','LED_Diffuser_Ring']
trees = {n: bvh(bpy.data.objects[n]) for n in sorted(set(names)) if bpy.data.objects.get(n)}
for a in sorted(trees):
    for b in sorted(trees):
        if a >= b: continue
        n = len(trees[a].overlap(trees[b]))
        if n:
            print(f"OVERLAP {a:20s} x {b:20s} {n}")
print("done")
