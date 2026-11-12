import bpy, os

OUT = r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5\blender\_work"

def prof(name, col):
    path = os.path.join(OUT, name)
    img = bpy.data.images.load(path)
    w, h = img.size
    px = list(img.pixels)
    rows = []
    for yt in range(360, 541):
        i = ((h - 1 - yt) * w + col) * 4
        lum = 0.2126 * px[i] + 0.7152 * px[i + 1] + 0.0722 * px[i + 2]
        rows.append((yt, lum))
    # detect local extrema relative to a 31px moving median
    import statistics
    vals = [l for _, l in rows]
    out = []
    for k in range(15, len(vals) - 15):
        win = sorted(vals[k - 15:k + 16])
        med = win[len(win) // 2]
        d = vals[k] - med
        if abs(d) > 0.0012:
            out.append((rows[k][0], round(vals[k], 4), round(d, 4)))
    print(f'--- {name} col={col}')
    print('  anomalies (row, lum, delta):', out[:24])
    print('  sample:', ' '.join(f'{rows[k][0]}:{vals[k]:.3f}' for k in range(15, len(vals) - 15, 12)))

for name in ('r6_flat_seam.png', 'r9_weld_seam.png', 'r11_seam.png'):
    prof(name, 800)
print('DONE')
