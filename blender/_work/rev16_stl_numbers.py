import os, struct, math
ROOT = r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\stl\v3'
for fn in sorted(os.listdir(ROOT)):
    if not fn.lower().endswith('.stl'):
        continue
    p = os.path.join(ROOT, fn)
    with open(p, 'rb') as f:
        head = f.read(84)
        n = struct.unpack('<I', head[80:84])[0]
        vs = []
        vol = 0.0
        for i in range(n):
            rec = f.read(50)
            vals = struct.unpack('<12fH', rec)
            a = vals[3:6]; b = vals[6:9]; c = vals[9:12]
            vs += [a, b, c]
            vol += (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0]))/6.0
    xs = [v[0] for v in vs]; ys = [v[1] for v in vs]; zs = [v[2] for v in vs]
    print(f'{fn:26s} tris={n:6d} vol={vol:9.1f} bbox={max(xs)-min(xs):7.2f}x{max(ys)-min(ys):7.2f}x{max(zs)-min(zs):7.2f} z=[{min(zs):6.2f},{max(zs):6.2f}]')
