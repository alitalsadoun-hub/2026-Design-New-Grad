"""SCENTRO carousel slide builder (editable source). Usage: python3 build_slide.py 1"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1350
CORM = 'fonts/CormorantGaramond-VF.ttf'
INTER = '/usr/share/fonts/opentype/inter/Inter-Regular.otf'
INTER_M = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'
rng = np.random.default_rng(7)

def S(title, mad, orig, inspired, title_rgb, bg_a, bg_b, arch_rgb, mad_h=600, orig_h=440, sink=0, name_size=46):
    return dict(title=title, mad=f'assets/cutouts/{mad}.png', orig=f'assets/cutouts/{orig}.png', inspired=inspired,
                title_rgb=title_rgb, bg_a=bg_a, bg_b=bg_b, arch_rgb=arch_rgb, mad_h=mad_h, orig_h=orig_h, sink=sink,
                name_size=name_size, out=f'output/slide{{n}}_{title.lower()}.png')

SLIDES = {
 1: S('ROUGE', 'mad_rouge', 'brx540_extrait', 'Baccarat Rouge 540 Extrait de Parfum', (122, 20, 38), (244, 236, 223), (230, 216, 196), (228, 213, 192), name_size=40),
 2: S('TREASURE', 'mad_treasure', 'naxos', 'Naxos', (142, 98, 34), (245, 236, 218), (232, 214, 184), (230, 212, 182), mad_h=590, orig_h=470),
 3: S('MARJORIE', 'mad_marjorie', 'guidance', 'Guidance', (148, 86, 92), (246, 239, 230), (236, 220, 212), (232, 214, 205), mad_h=590, orig_h=360),
 4: S('EFFECT', 'mad_effect', 'side_effect', 'Side Effect', (104, 30, 38), (243, 234, 221), (228, 211, 193), (226, 207, 188), mad_h=600, orig_h=440),
 5: S('DREAMLIGHT', 'mad_dreamlight', 'attrape_reves', 'Attrape-Rêves', (126, 88, 130), (247, 241, 239), (235, 224, 231), (232, 218, 222), mad_h=540, orig_h=440),
 6: S('FORZA', 'mad_forza', 'alexandria_ii', 'Alexandria II', (106, 74, 42), (244, 236, 222), (229, 214, 190), (228, 211, 184), mad_h=500, orig_h=470),
}

def font(path, size, var=None):
    f = ImageFont.truetype(path, size)
    if var: f.set_variation_by_name(var)
    return f

def tracked(draw, cx, cy, text, f, fill, track):
    """Draw letter-spaced text centred on (cx, cy) (cy = vertical middle)."""
    ws = [draw.textlength(c, font=f) for c in text]
    total = sum(ws) + track * (len(text) - 1)
    x = cx - total / 2
    for c, w in zip(text, ws):
        draw.text((x, cy), c, font=f, fill=fill, anchor='lm'); x += w + track

def background(a, b):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = np.clip((xx / W * 0.45 + yy / H * 0.75), 0, 1)[..., None]
    a = np.array(a, np.float32); b = np.array(b, np.float32)
    img = a * (1 - t) + b * t
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')

def arch(img, base_rgb):
    cx, top, bot, R = 540, 500, 1115, 340
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    d.ellipse((cx - R, top, cx + R, top + 2 * R), fill=255); d.rectangle((cx - R, top + R, cx + R, bot), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(0.8))
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    xx = np.linspace(-1, 1, W, dtype=np.float32)[None, :]
    base = np.array(base_rgb, np.float32)
    shade = (1 - 0.10 * np.abs(xx) - 0.05 * np.clip((yy - 0.6) / 0.4, 0, 1))[..., None]
    fill = Image.fromarray(np.clip(base * shade * np.ones((H, W, 3), np.float32), 0, 255).astype(np.uint8)).convert('RGBA')
    img.paste(fill, (0, 0), m)
    # soft inner rim on the arch edge
    rim = Image.new('L', (W, H), 0); ImageDraw.Draw(rim).arc((cx - R, top, cx + R, top + 2 * R), 180, 360, fill=255, width=3)
    ImageDraw.Draw(rim).line((cx - R, top + R, cx - R, bot), fill=255, width=3); ImageDraw.Draw(rim).line((cx + R, top + R, cx + R, bot), fill=255, width=3)
    rim = rim.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: int(v * 0.55))
    img.paste(Image.new('RGBA', (W, H), (205, 180, 145, 255)), (0, 0), rim)

def travertine(img, y0=1112, ledge=34):
    h = H - y0
    base = np.zeros((h, W, 3), np.float32)
    base[:ledge] = (238, 225, 203); base[ledge:] = (200, 186, 166)
    from scipy.ndimage import gaussian_filter
    streak = gaussian_filter(rng.normal(0, 1, (h, 1)), (2, 0)).repeat(W, 1) * 2.5
    base += (streak * 6)[..., None]
    base += rng.normal(0, 1.6, (h, W, 1))
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    # pits / fills
    d = ImageDraw.Draw(im)
    for _ in range(300):
        x = rng.integers(0, W); y = rng.integers(0, h); l = rng.integers(4, 22); t = rng.integers(1, 4)
        c = tuple(int(v) for v in (rng.choice([178, 224]) * np.ones(3) * np.array([1, .95, .88])))
        d.ellipse((x, y, x + l, y + t), fill=c)
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    img.paste(im.convert('RGBA'), (0, y0))
    # ledge highlight + contact darkening
    d = ImageDraw.Draw(img)
    d.line((0, y0, W, y0), fill=(246, 238, 222, 255), width=2)
    d.line((0, y0 + ledge, W, y0 + ledge), fill=(176, 160, 140, 255), width=2)

def place(img, path, cx, base_y, height, shadow_dx=26, shadow_w=1.0):
    b = Image.open(path).convert('RGBA')
    w = round(b.width * height / b.height)
    b = b.resize((w, height), Image.LANCZOS)
    x = round(cx - w / 2); y = base_y - height
    # contact shadow + soft cast shadow
    sh = Image.new('L', (W, H), 0); d = ImageDraw.Draw(sh)
    d.ellipse((x - 6, base_y - 12, x + w + 6, base_y + 16), fill=190)
    sh1 = sh.filter(ImageFilter.GaussianBlur(9))
    cast = Image.new('L', (W, H), 0); d = ImageDraw.Draw(cast)
    d.ellipse((x + w * 0.35 + shadow_dx, base_y - 20, x + w * (1.1 + 0.55 * shadow_w) + shadow_dx, base_y + 22), fill=110)
    cast = cast.filter(ImageFilter.GaussianBlur(20))
    dark = Image.new('RGBA', (W, H), (92, 70, 52, 255))
    img.paste(dark, (0, 0), cast.point(lambda v: int(v * .55)))
    img.paste(dark, (0, 0), sh1.point(lambda v: int(v * .75)))
    img.alpha_composite(b, (x, y))
    return x, y, w

def build(n):
    s = SLIDES[n]; s['out'] = s['out'].format(n=n)
    img = background(s['bg_a'], s['bg_b']); arch(img, s['arch_rgb']); travertine(img)
    d = ImageDraw.Draw(img)
    brown = (74, 52, 40); gold = (176, 141, 87)
    # logo (placeholder wordmark until the real file is supplied)
    tracked(d, 540, 90, 'SCENTRO', font(CORM, 42, 'Medium'), brown, 20)
    tracked(d, 540, 125, 'LOGO PLACEHOLDER', font(INTER, 11), (176, 150, 125), 5.5)
    d.line((517, 156, 563, 156), fill=gold, width=2)
    # title block
    size = 100
    while True:
        tf = font(CORM, size, 'SemiBold'); tw = sum(d.textlength(c, font=tf) for c in s['title']) + (size * .12) * (len(s['title']) - 1)
        if tw <= 720 or size < 50: break
        size -= 2
    tracked(d, 540, 243, s['title'], tf, s['title_rgb'], size * .12)
    tracked(d, 540, 317, 'MAD PARFUMEUR', font(INTER, 20), brown, 9)
    d.line((480, 350, 600, 350), fill=gold, width=2); d.ellipse((536, 346, 544, 354), fill=gold)
    # INSPIRED BY – darker champagne-gold, slightly heavier than draft for contrast
    tracked(d, 540, 377, 'INSPIRED BY', font(INTER_M, 16), (143, 105, 52), 8)
    ns = s['name_size']
    while sum(d.textlength(c, font=font(CORM, ns, 'SemiBold')) for c in s['inspired']) + 1.5 * len(s['inspired']) > 700: ns -= 2
    tracked(d, 540, 425, s['inspired'], font(CORM, ns, 'SemiBold'), brown, 1.5)
    # bottles: MAD larger left, original smaller right, shared baseline on the ledge
    base = 1128; gap = 56
    def dims(p, h):
        im = Image.open(p); return round(im.width * h / im.height)
    w1, w2 = dims(s['mad'], s['mad_h']), dims(s['orig'], s['orig_h'])
    left = 540 - (w1 + gap + w2) / 2
    place(img, s['mad'], left + w1 / 2, base, s['mad_h'])
    place(img, s['orig'], left + w1 + gap + w2 / 2, base + s['sink'], s['orig_h'], shadow_dx=14, shadow_w=0.6)
    out = img.convert('RGB'); out.save(s['out'], optimize=True); print(s['out'], out.size)

if __name__ == '__main__':
    build(int(sys.argv[1]))
