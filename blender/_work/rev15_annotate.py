import json, os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = r'C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5'
REV = os.path.join(ROOT, 'blender', '_review')
DES = os.path.join(ROOT, 'design')
FONT_B = r'C:\Windows\Fonts\msyhbd.ttc'
FONT_R = r'C:\Windows\Fonts\msyh.ttc'
GOLD = (232, 181, 102, 255)
WHITE = (246, 248, 251, 255)
MUTED = (178, 190, 204, 255)
PANEL = (10, 16, 25, 232)
PANEL_EDGE = (232, 181, 102, 210)

def F(sz, bold=True):
    return ImageFont.truetype(FONT_B if bold else FONT_R, sz)

def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0], b[3] - b[1]

def anchor_of(name, key):
    p = os.path.join(REV, 'anchors_' + name + '.json')
    d = json.load(open(p, encoding='utf-8'))
    return tuple(d['anchors'][key])

def rounded(d, box, r, fill, outline=None, width=2):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def draw_label(img, box_center, title, sub, num, anchor, f_title, f_sub, max_w=None):
    d = ImageDraw.Draw(img, 'RGBA')
    pad_x, pad_y, gap = 24, 16, 6
    badge = 46
    w1, h1 = tw(d, title, f_title)
    w2, h2 = tw(d, sub, f_sub) if sub else (0, 0)
    text_w = max(w1, w2)
    box_w = badge + 16 + text_w + pad_x * 2
    box_h = max(badge, h1 + (gap + h2 if sub else 0)) + pad_y * 2
    cx, cy = box_center
    left, top = cx - box_w / 2, cy - box_h / 2
    right, bottom = left + box_w, top + box_h
    # shadow
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.rounded_rectangle((left + 7, top + 9, right + 7, bottom + 9), radius=16, fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    img.alpha_composite(sh)
    d = ImageDraw.Draw(img, 'RGBA')
    rounded(d, (left, top, right, bottom), 16, PANEL, PANEL_EDGE, 2)
    bx = left + pad_x + badge / 2
    by = top + box_h / 2
    d.ellipse((bx - badge / 2, by - badge / 2, bx + badge / 2, by + badge / 2), fill=GOLD)
    nf = F(26, True)
    nw, nh = tw(d, str(num), nf)
    d.text((bx - nw / 2, by - nh / 2 - 4), str(num), font=nf, fill=(12, 18, 28, 255))
    tx = left + pad_x + badge + 16
    ty = top + pad_y - 2
    d.text((tx, ty), title, font=f_title, fill=WHITE)
    if sub:
        d.text((tx, ty + h1 + gap), sub, font=f_sub, fill=MUTED)
    # leader side
    ax, ay = anchor
    if ax < left:
        sx, sy = left, min(max(ay, top + 14), bottom - 14)
    elif ax > right:
        sx, sy = right, min(max(ay, top + 14), bottom - 14)
    elif ay < top:
        sx, sy = min(max(ax, left + 14), right - 14), top
    else:
        sx, sy = min(max(ax, left + 14), right - 14), bottom
    if abs(ax - sx) > abs(ay - sy):
        mx = sx + (ax - sx) * 0.55
        pts = [(sx, sy), (mx, sy), (mx, ay), (ax, ay)]
    else:
        my = sy + (ay - sy) * 0.55
        pts = [(sx, sy), (sx, my), (ax, my), (ax, ay)]
    d.line(pts, fill=GOLD, width=4, joint='curve')
    # arrowhead
    x1, y1 = pts[-2]
    ang = math.atan2(ay - y1, ax - x1)
    L, W = 20, 9
    p1 = (ax - L * math.cos(ang) + W * math.sin(ang), ay - L * math.sin(ang) - W * math.cos(ang))
    p2 = (ax - L * math.cos(ang) - W * math.sin(ang), ay - L * math.sin(ang) + W * math.cos(ang))
    d.polygon([ (ax, ay), p1, p2 ], fill=GOLD)
    d.ellipse((ax - 11, ay - 11, ax + 11, ay + 11), outline=GOLD, width=3)
    d.ellipse((ax - 4, ay - 4, ax + 4, ay + 4), fill=WHITE)

def note_panel(img, xy, lines, w=760, title=None, f_title=None, f_body=None):
    d = ImageDraw.Draw(img, 'RGBA')
    x, y = xy
    f_title = f_title or F(28, True)
    f_body = f_body or F(21, False)
    pad = 26
    h = pad * 2 + (52 if title else 0) + len(lines) * 36
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=(10, 16, 25, 220), outline=(232, 181, 102, 150), width=2)
    yy = y + pad
    if title:
        d.text((x + pad, yy), title, font=f_title, fill=GOLD)
        yy += 52
    for ln in lines:
        d.text((x + pad, yy), ln, font=f_body, fill=(215, 223, 232, 255))
        yy += 36

def title_block(img, kicker, title, sub, f_kick=None, f_t=None, f_s=None, x=64, y=52):
    d = ImageDraw.Draw(img, 'RGBA')
    f_kick = f_kick or F(26, True)
    f_t = f_t or F(58, True)
    f_s = f_s or F(26, False)
    d.rectangle((x, y + 4, x + 8, y + 46), fill=GOLD)
    d.text((x + 22, y), kicker, font=f_kick, fill=GOLD)
    d.text((x + 20, y + 40), title, font=f_t, fill=WHITE)
    d.text((x + 22, y + 40 + tw(d, title, f_t)[1] + 22), sub, font=f_s, fill=MUTED)

def open_rgba(name):
    return Image.open(os.path.join(REV, name)).convert('RGBA')

# ---------------- Figure 1: external parts ----------------
def fig1():
    img = open_rgba('70_hero_label.png')
    f_t, f_s = F(38, True), F(23, False)
    title_block(img, 'REV 3 · 装配指示  1 / 5', '整机外部零件',
                'ESP32 桌宠外壳 ｜ 打印件 11 种 15 件 ｜ 可拆耳/尾 ｜ 无头版', F(26, True), F(60, True), F(27, False))
    items = [
        ('机身主体', 'Enclosure Body ×1', 1, anchor_of('70_hero_label', 'body'), (330, 1045)),
        ('顶盖', 'Lid ×1 · 重力定位，免螺丝', 2, anchor_of('70_hero_label', 'lid'), (300, 620)),
        ('LED 导光环', 'Diffuser Ring ×1', 3, anchor_of('70_hero_label', 'ring'), (2280, 700)),
        ('前脸面板', 'Face Plate ×1 · 4×M2×6', 4, anchor_of('70_hero_label', 'face'), (2255, 1305)),
        ('摆腿 ×4', '左右各 2 · 4×M2×10', 5, anchor_of('70_hero_label', 'leg'), (1780, 1725)),
        ('顶部按键 ×3', '上 / 左 / 右', 6, anchor_of('70_hero_label', 'button'), (1460, 300)),
        ('狗耳 ×2', '可拆插接', 7, anchor_of('70_hero_label', 'ear'), (1920, 430)),
        ('尾巴', '加长版 · 可拆插接', 8, anchor_of('70_hero_label', 'tail'), (480, 390)),
    ]
    for t, s, n, a, b in items:
        draw_label(img, b, t, s, n, a, f_t, f_s)
    img.convert('RGB').save(os.path.join(DES, 'enclosure-v3-parts-overview.png'), quality=95)
    print('fig1 done')

# ---------------- Figure 2: exploded shell ----------------
def fig2():
    img = open_rgba('71_exploded_shell.png')
    f_t, f_s = F(38, True), F(23, False)
    title_block(img, 'REV 3 · 装配指示  2 / 5', '壳体分解图',
                '分解层级：底腹板 → 机身 → 前脸 → 顶盖 → 导光环；摆腿从四角装入', F(26, True), F(58, True), F(26, False))
    items = [
        ('顶盖', 'Lid ×1 · 先装按键/触摸/耳尾', 1, anchor_of('71_exploded_shell', 'lid'), (300, 420)),
        ('LED 导光环', 'Diffuser Ring ×1 · 最后压入', 2, anchor_of('71_exploded_shell', 'ring'), (1880, 330)),
        ('机身主体', 'Enclosure Body ×1', 3, anchor_of('71_exploded_shell', 'body'), (260, 1080)),
        ('前脸面板', 'Face Plate ×1 · 4×M2×6', 4, anchor_of('71_exploded_shell', 'face'), (2110, 1140)),
        ('底腹板', 'Belly Pan ×1 · 6×M2×8', 5, anchor_of('71_exploded_shell', 'pan'), (1050, 1880)),
        ('摆腿 ×4', '左右各 2 · 4×M2×10', 6, anchor_of('71_exploded_shell', 'leg_fr'), (430, 1650)),
    ]
    for t, s, n, a, b in items:
        draw_label(img, b, t, s, n, a, f_t, f_s)
    img.convert('RGB').save(os.path.join(DES, 'enclosure-v3-exploded-labeled.png'), quality=95)
    print('fig2 done')

# ---------------- Figure 3: lid underside with legend ----------------
def fig3():
    base = open_rgba('72_lid_under_label.png')
    W, H = base.size
    strip = 300
    canvas = Image.new('RGBA', (W, H + strip), (10, 16, 25, 255))
    canvas.alpha_composite(base, (0, 0))
    d = ImageDraw.Draw(canvas, 'RGBA')
    d.line((0, H, W, H), fill=(232, 181, 102, 120), width=2)
    # markers
    items = [
        ('顶盖唇边', '内唇 0.3 定位 · 免螺丝', anchor_of('72_lid_under_label', 'lip')),
        ('按键 ×3', '从顶盖内侧装入，帽朝外', anchor_of('72_lid_under_label', 'buttons')),
        ('耳 / 尾插接座', '3 处压配座 · 可拆', anchor_of('72_lid_under_label', 'ear_r')),
        ('触摸模块', '贴装于顶盖内侧 · 4-pin', (1457, 590)),
    ]
    f_num = F(28, True); f_t = F(30, True); f_s = F(21, False)
    colw = W // 4
    for i, (t, s, a) in enumerate(items, 1):
        ax, ay = a
        d.ellipse((ax - 26, ay - 26, ax + 26, ay + 26), fill=(10, 16, 25, 235), outline=GOLD, width=3)
        nw, nh = tw(d, str(i), f_num)
        d.text((ax - nw / 2, ay - nh / 2 - 3), str(i), font=f_num, fill=GOLD)
        cx = colw * (i - 0.5)
        d.ellipse((cx - 130 - 20, H + 42, cx - 130 + 20, H + 82), fill=GOLD)
        nw, nh = tw(d, str(i), F(24, True))
        d.text((cx - 130 - nw / 2, H + 42 + 20 - nh / 2 - 3), str(i), font=F(24, True), fill=(12, 18, 28, 255))
        d.text((cx - 100, H + 38), t, font=f_t, fill=WHITE)
        d.text((cx - 100, H + 80), s, font=f_s, fill=MUTED)
    title_block(canvas, 'REV 3 · 装配指示  3 / 5', '顶盖内侧装配',
                '按键从内侧穿过；触摸模块贴装于顶盖内表面；耳/尾为压配插接', F(24, True), F(46, True), F(23, False), x=54, y=42)
    canvas.convert('RGB').save(os.path.join(DES, 'enclosure-v3-lid-labeled.png'), quality=95)
    print('fig3 done')

# ---------------- Figure 4: internal layout ----------------
def fig4():
    img = open_rgba('73_int_label.png')
    f_t, f_s = F(34, True), F(21, False)
    title_block(img, 'REV 3 · 装配指示  4 / 5', '内部布局',
                '主控板位于舵机舱上方；电池在下层后部；喇叭居中；OLED 竖直插在前脸', F(24, True), F(50, True), F(23, False))
    items = [
        ('ESP32 主控板', 'PCB ×1 · 4×M2 铜柱/卡扣', 1, anchor_of('73_int_label', 'pcb'), (360, 480)),
        ('1.3″ OLED', 'I²C 4-pin · 嵌入前脸', 2, anchor_of('73_int_label', 'oled'), (1600, 340)),
        ('103450 锂电池', '后部下层 · 1000 mAh', 3, anchor_of('73_int_label', 'battery'), (360, 1090)),
        ('3070 腔体喇叭', '居中 · 顶盖格栅出音', 4, (1170, 900), (1000, 1350)),
        ('SG90 舵机 ×4', '卧式滑入四角舵机舱', 5, anchor_of('73_int_label', 'servo'), (1700, 760)),
        ('摆腿 ×4', '舵盘外露 · 4×M2×10', 6, anchor_of('73_int_label', 'leg'), (1710, 1110)),
    ]
    for t, s, n, a, b in items:
        draw_label(img, b, t, s, n, a, f_t, f_s)
    img.convert('RGB').save(os.path.join(DES, 'enclosure-v3-internal-labeled.png'), quality=95)
    print('fig4 done')

# ---------------- Figure 5: screw map ----------------
def fig5():
    views = []
    specs = [
        ('80_screw_front', '前脸面板 · 4 颗 M2×6 平头/沉头', (650, 40, 40)),
        ('81_screw_bottom', '底腹板 · 6 颗 M2×8 圆头（从底部看，上=前）', (650, 40, 40)),
        ('82_screw_side', '摆腿 · 4 颗 M2×10 圆头（本侧 2 颗）', (650, 40, 40)),
    ]
    W, H = 2700, 2450
    canvas = Image.new('RGB', (W, H), (13, 18, 26))
    d = ImageDraw.Draw(canvas, 'RGBA')
    d.rectangle((0, 0, W, 150), fill=(9, 14, 21, 255))
    d.rectangle((54, 40, 62, 108), fill=GOLD)
    d.text((84, 34), 'REV 3 · 装配指示  5 / 5', font=F(25, True), fill=GOLD)
    d.text((82, 66), '螺丝装配图 · 共 14 颗', font=F(54, True), fill=WHITE)
    d.text((W - 760, 55), '0 颗：舵机 / 顶盖 / 导光环 / 耳尾', font=F(25, True), fill=(214, 222, 232, 255))
    d.text((W - 760, 92), '舵机靠舱位+腿螺丝固定；顶盖为重力定位', font=F(22, False), fill=MUTED)
    tiles = []
    positions = [(60, 190), (1380, 190), (60, 1170)]
    for (name, cap, *_ ), (tx, ty) in zip(specs, positions):
        im = Image.open(os.path.join(REV, name + '.png')).convert('RGB')
        im.thumbnail((1240, 900), Image.LANCZOS)
        tile = Image.new('RGB', (1240, 940), (15, 21, 30))
        td = ImageDraw.Draw(tile, 'RGBA')
        td.text((30, 14), cap, font=F(28, True), fill=WHITE)
        tile.paste(im, ((1240 - im.width) // 2, 60))
        canvas.paste(tile, (tx, ty))
        anchors = json.load(open(os.path.join(REV, 'anchors_' + name + '.json'), encoding='utf-8'))
        sx = im.width / anchors['res'][0]; sy = im.height / anchors['res'][1]
        ox = tx + (1240 - im.width) // 2; oy = ty + 60
        for k, (ax, ay) in anchors['anchors'].items():
            px, py = ox + ax * sx, oy + ay * sy
            d.ellipse((px - 20, py - 20, px + 20, py + 20), outline=GOLD, width=3)
            d.line((px - 12, py, px + 12, py), fill=GOLD, width=3)
            d.line((px, py - 12, px, py + 12), fill=GOLD, width=3)
    # summary panel
    px, py = 1380, 1170
    panel = Image.new('RGBA', (1240, 1140), (17, 24, 34, 255))
    pd = ImageDraw.Draw(panel, 'RGBA')
    pd.rounded_rectangle((0, 0, 1240, 1140), radius=18, fill=(17, 24, 34, 255), outline=(232, 181, 102, 160), width=2)
    pd.text((40, 34), '螺丝清单', font=F(38, True), fill=WHITE)
    pd.line((40, 96, 1200, 96), fill=(70, 82, 96, 255), width=2)
    rows = [
        ('前脸面板', 'M2×6 平头/沉头', 'M2×6', '4', '≤4.5 上限', '正面四角'),
        ('底腹板', 'M2×8 圆头/盘头', 'M2×8', '6', '≈6.7 mm', '沉孔 · 底部六点'),
        ('四条摆腿', 'M2×10 圆头', 'M2×10', '4', '≈3.6 mm', '舵机输出轴'),
    ]
    colx = [40, 280, 550, 700, 810, 980]
    heads = ['位置', '规格', '长度', '数量', '旋合', '备注']
    for i, h in enumerate(heads):
        pd.text((colx[i], 120), h, font=F(22, True), fill=GOLD)
    y = 168
    for row in rows:
        for i, c in enumerate(row):
            pd.text((colx[i], y), c, font=F(24, False), fill=(225, 231, 238, 255))
        y += 58
    pd.line((40, y + 10, 1200, y + 10), fill=(70, 82, 96, 255), width=2)
    pd.text((40, y + 38), '合计', font=F(31, True), fill=WHITE)
    pd.text((160, y + 26), '14 颗', font=F(52, True), fill=GOLD)
    pd.text((400, y + 40), '备件：M2×6 ×2、M2×8 ×2、M2×10 ×1', font=F(24, False), fill=MUTED)
    tips = [
        '工具：PH0 十字螺丝刀；扭矩 0.10–0.15 N·m，手拧到位后再轻紧 1/8 圈。',
        '塑料自攻孔：先逆时针退半圈找牙，再顺时针拧入；不要用电动批高速拧。',
        '前脸 M2×6 已是上限（孔深 4.5）：螺丝头顶不到底时锉短 0.3 mm 或换 M2×5；滑牙改 M2.2，切勿 M2×8。',
        '底腹板为电池检修口：M2×8 圆头配 1.5 mm 沉孔，10.9 mm 深孔可反复拆装。',
        '摆腿螺丝拧到轻触舵机壳体即停；若到底，退 1/4 圈，避免压裂舵盘。',
        '底视图方向：上=前；从底部仰视时，前后方向与俯视图相反。',
    ]
    ty = y + 120
    for t in tips:
        pd.text((40, ty), '·', font=F(24, True), fill=GOLD)
        pd.text((62, ty), t, font=F(21, False), fill=(205, 214, 224, 255))
        ty += 42
    canvas.paste(panel, (px, py))
    canvas.save(os.path.join(DES, 'enclosure-v3-screws.png'), quality=95)
    print('fig5 done')

# ---------------- Figure 6: tail printing ----------------
def fig6():
    img = open_rgba('83_tail_print.png')
    f_t, f_s = F(34, True), F(22, False)
    title_block(img, 'REV 3 · 打印件', '尾巴 · 加长版',
                'STL 原方向：底座贴床；打印高度 28.7 mm，摆尾更明显', F(24, True), F(50, True), F(24, False))
    note_panel(img, (920, 300), [
        '底座贴床，STL 原方向直接打印',
        '尾管悬空段与圆球下方加树状支撑',
        '支撑痕留在底面/尾管下方，拆后砂纸打磨',
        '建议 0.16–0.2 mm 层高，壁厚 ≥3 圈',
    ], w=640, title='打印要点')
    draw_label(img, (400, 480), '尾巴本体', '弧线加长 · 顶端圆球', 1, (717, 820), f_t, f_s)
    draw_label(img, (1120, 1150), '底座插接柱', '压入顶盖尾座', 2, (800, 1045), f_t, f_s)
    img.convert('RGB').save(os.path.join(DES, 'enclosure-v3-tail-print.png'), quality=95)
    print('fig6 done')

if __name__ == '__main__':
    fig1(); fig2(); fig3(); fig4(); fig5(); fig6()
