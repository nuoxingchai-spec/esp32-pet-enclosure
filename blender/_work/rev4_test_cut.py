import bpy, bmesh, math
from mathutils import Vector

F = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\robot_dog_enclosure_v3.blend"
bpy.ops.wm.open_mainfile(filepath=F)
sc = bpy.context.scene
body = bpy.data.objects['Enclosure_Body']
mw = body.matrix_world; mi = mw.inverted()
M3 = mw.to_3x3(); M3i = M3.inverted()
dg = bpy.context.evaluated_depsgraph_get()

# duplicate body
dup = body.copy(); dup.data = body.data.copy(); dup.name = 'BODY_TEST'
sc.collection.objects.link(dup)
dup.matrix_world = mw.copy()
body.hide_viewport = True; body.hide_render = True
dup.select_set(True); bpy.context.view_layer.objects.active = dup

# corner frame
CX, CY = 30.0, -55.0
def ray_r(z, th_deg, back=60.0):
    th = math.radians(th_deg)
    ux, uy = math.cos(th), -math.sin(th)
    org = mi @ Vector((CX + back*ux, CY + back*uy, z))
    d = (M3i @ Vector((-ux, -uy, 0))).normalized()
    ok, loc, nor, idx = body.ray_cast(org, d, distance=300.0, depsgraph=dg)
    if not ok: return None
    p = mw @ loc
    return math.hypot(p.x-CX, p.y-CY)

THS = [ -12 + i*2 for i in range(37) ]           # -12..60
ZS  = [49.0,49.5,50.0,50.5,51.0,51.5,52.0,52.5,53.0,53.5,54.0,54.2,54.3,54.34,54.35,54.36,54.5,55.0,56.0,57.0,58.0,59.0,60.0]
R_OUT = 42.0
def smooth(t):
    t=max(0.0,min(1.0,t)); return t*t*(3-2*t)
def clear(th):
    if th < 0: return 0.12*smooth(-th/12.0)
    if th > 45: return 0.12*smooth((th-45)/15.0)
    return 0.0

tabL={}; tabU={}
for th in THS:
    tabL[th]=ray_r(52.0, th); tabU[th]=ray_r(56.0, th)
    if tabL[th] is None or tabU[th] is None:
        print('MISS', th); raise SystemExit(1)

rows=[]
for j,z in enumerate(ZS):
    row=[]
    for th in THS:
        if z <= 54.35:
            s = smooth((z-49.0)/5.35)
            r = tabL[th] + s*(tabU[th]-tabL[th]) + clear(th)
        else:
            r = tabU[th] + 0.12
        a = math.radians(th)
        row.append((CX + r*math.cos(a), CY - r*math.sin(a), z))
    rows.append(row)

bm = bmesh.new()
V_in = [[bm.verts.new(p) for p in row] for row in rows]
V_out = [[bm.verts.new((CX + R_OUT*math.cos(math.radians(th)), CY - R_OUT*math.sin(math.radians(th)), z)) for th in THS] for z in ZS]
NI, NJ = len(THS), len(ZS)
for j in range(NJ-1):
    for i in range(NI-1):
        bm.faces.new((V_in[j][i], V_in[j][i+1], V_in[j+1][i+1], V_in[j+1][i]))
        bm.faces.new((V_out[j][i], V_out[j+1][i], V_out[j+1][i+1], V_out[j][i+1]))
for i in range(NI-1):
    bm.faces.new((V_in[0][i], V_out[0][i], V_out[0][i+1], V_in[0][i+1]))
    bm.faces.new((V_in[NJ-1][i], V_in[NJ-1][i+1], V_out[NJ-1][i+1], V_out[NJ-1][i]))
for j in range(NJ-1):
    bm.faces.new((V_in[j][0], V_in[j+1][0], V_out[j+1][0], V_out[j][0]))
    bm.faces.new((V_in[j][NI-1], V_out[j][NI-1], V_out[j+1][NI-1], V_in[j+1][NI-1]))
bm.normal_update()
nm = sum(1 for e in bm.edges if len(e.link_faces)!=2)
print('CUTTER verts', len(bm.verts), 'faces', len(bm.faces), 'nm_edges', nm, 'volume', round(bm.calc_volume(signed=True),1))
cut_me = bpy.data.meshes.new('Cutter_test'); bm.to_mesh(cut_me); bm.free()
cut = bpy.data.objects.new('Cutter_test', cut_me); sc.collection.objects.link(cut)

mod = dup.modifiers.new('shoulder','BOOLEAN')
mod.operation='DIFFERENCE'; mod.solver='MANIFOLD'; mod.object=cut
bpy.context.view_layer.objects.active = dup
try:
    bpy.ops.object.modifier_apply(modifier=mod.name)
    print('APPLIED manifold solver')
except Exception as e:
    print('MANIFOLD failed', e)
    dup.modifiers.clear()
    mod = dup.modifiers.new('shoulder','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cut
    bpy.ops.object.modifier_apply(modifier=mod.name)
    print('APPLIED exact solver')

bm2 = bmesh.new(); bm2.from_mesh(dup.data)
nm = sum(1 for e in bm2.edges if len(e.link_faces)!=2)
bnd = sum(1 for e in bm2.edges if len(e.link_faces)<2)
zero = sum(1 for f in bm2.faces if f.calc_area() < 1e-9)
# components
bm2.verts.ensure_lookup_table()
par=list(range(len(bm2.verts)))
def find(a):
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
for e in bm2.edges:
    a,b=find(e.verts[0].index),find(e.verts[1].index)
    if a!=b: par[a]=b
comps=len({find(i) for i in range(len(bm2.verts))})
print('AFTER v',len(bm2.verts),'f',len(bm2.faces),'nm',nm,'bnd',bnd,'zero',zero,'comps',comps)
zs=[v.co.z for v in bm2.verts]; xs=[v.co.x for v in bm2.verts]; ys=[v.co.y for v in bm2.verts]
print('bbox local x',round(min(xs),2),round(max(xs),2),'y',round(min(ys),2),round(max(ys),2),'z',round(min(zs),2),round(max(zs),2))
bm2.free()

# profile after cut
dg2 = bpy.context.evaluated_depsgraph_get()
dup_mw = dup.matrix_world; dup_mi = dup_mw.inverted(); D3=dup_mw.to_3x3(); D3i=D3.inverted()
def ray_dup(z, th_deg):
    th=math.radians(th_deg); ux,uy=math.cos(th),-math.sin(th)
    org=dup_mi @ Vector((CX+60*ux, CY+60*uy, z))
    d=(D3i @ Vector((-ux,-uy,0))).normalized()
    ok,loc,nor,idx=dup.ray_cast(org,d,distance=300.0,depsgraph=dg2)
    if not ok: return None
    p=dup_mw @ loc
    return math.hypot(p.x-CX,p.y-CY)
print('post-cut r(theta): z=50/52/54.34/54.5/56 vs upper')
for z in [50.0,52.0,54.34,54.5,56.0]:
    row=[]
    for th in [-12,-6,0,10,20,30,35,40,45,50,60]:
        r=ray_dup(z,th)
        row.append('  --  ' if r is None else f"{r:6.3f}")
    print(f'z{z:6.2f} '+' '.join(row))
print('cols -12    -6     0    10    20    30    35    40    45    50    60')

sc.render.engine='BLENDER_WORKBENCH'
sh=sc.display.shading
sh.light='STUDIO'; sh.studio_light='Default'; sh.color_type='OBJECT'
sh.show_cavity=True; sh.cavity_type='BOTH'; sh.curvature_ridge_factor=2.0; sh.curvature_valley_factor=2.0
sh.show_shadows=True; sh.shadow_intensity=0.35
sc.world.color=(0.82,0.85,0.9)
sc.render.resolution_x=1000; sc.render.resolution_y=900
sc.render.image_settings.file_format='PNG'
for n in ['Enclosure_Lid','LED_Diffuser_Ring','Ear_L','Ear_R','Tail','Preview_Ground','Cutter_test']:
    o=bpy.data.objects.get(n)
    if o: o.hide_render=True
for o in bpy.data.objects:
    if o.name.startswith('Leg_'): o.hide_render=True
cam_d=bpy.data.cameras.new('C'); cam=bpy.data.objects.new('C',cam_d); sc.collection.objects.link(cam); sc.camera=cam
cam_d.lens=110
def look(pos,tgt):
    cam.location=pos; d=Vector(tgt)-Vector(pos); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
look((92,-78,60),(38.6,-60.2,51.5))
sc.render.filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev4_test_corner.png"
bpy.ops.render.render(write_still=True)
look((120,-52,54),(39,-58,50))
sc.render.filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev4_test_side.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work\rev4_test_cut.blend")
print('DONE')
