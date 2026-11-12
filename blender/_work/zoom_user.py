import bpy, numpy as np, os
base=r"C:\Users\admin\.qoder-cn\tmp\C--Users-admin-Documents-Qoder-2026-11-10-faf708e5\images\faf708e5-455a-4b8f-a7a0-23af2bc70018"
out=r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work"
items=[('dfcecad2-6d5b-4f9b-8c4c-1de56e8e1cdf.png','u1',(90,120,300,570),3),
       ('7c910701-e76d-442b-b27f-f2178c1c2acd.png','u2',(0,0,184,357),4)]
for fn,tag,crop,scale in items:
    im=bpy.data.images.load(os.path.join(base,fn))
    w,h=im.size
    a=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)
    a=a[::-1]  # top-down
    x0,y0,x1,y1=crop
    x0=max(0,x0); y0=max(0,y0); x1=min(w,x1); y1=min(h,y1)
    c=a[y0:y1,x0:x1]
    c=np.repeat(np.repeat(c,scale,axis=0),scale,axis=1)
    hh,ww=c.shape[:2]
    out_im=bpy.data.images.new(tag,width=ww,height=hh,alpha=True)
    out_im.pixels=c[::-1].ravel().tolist()
    p=os.path.join(out,tag+'.png'); out_im.filepath_raw=p; out_im.file_format='PNG'; out_im.save()
    print('WROTE',p,ww,hh)
