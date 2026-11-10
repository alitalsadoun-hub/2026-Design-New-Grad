"""SCENTRO Instagram Stories (1080x1920) - MAD New York Night + MAD Golden Soul.
Real product photographs (cut out, never redrawn) composited into a lit scene. Reuses the scene / shadow / edge-cleanup helpers of build_slide.py.
Safe zones: nothing important above y=250 or below y=1620.   Usage (from scentro/):  python3 stories/build_stories.py [nyn|gs ...]"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build_slide as B

W, H = 1080, 1920
SAFE_TOP, SAFE_BOT = 250, 1620
A = 'stories/assets/cutouts/'
CORM, INTER, INTER_M = B.CORM, B.INTER, B.INTER_M
rng = np.random.default_rng(21)


def canvas(arch_top, arch_r, surf_top, surf_front, base_y):
    B.H = H; B.ARCH_CX = 540; B.ARCH_TOP = arch_top; B.ARCH_R = arch_r
    B.SURF_TOP = surf_top; B.SURF_FRONT = surf_front; B.BASE_Y = base_y


def glow(img, cx, cy, rx, ry, rgb, alpha):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(1 - np.hypot((xx - cx) / rx, (yy - cy) / ry), 0, 1) ** 1.6 * alpha
    m = Image.fromarray((g * 255).astype(np.uint8))
    img.paste(Image.new('RGBA', (W, H), tuple(rgb) + (255,)), (0, 0), m)


def tracked_in(d, cx, cy, text, f, fill, track):
    B.tracked(d, cx, cy, text, f, fill, track)


def drop_shadow(img, item, x, y, dx=16, dy=11, blur=9, op=0.38, rgb=(86, 62, 46)):
    a = item.getchannel('A'); sh = Image.new('L', (W, H), 0); sh.paste(a, (x + dx, y + dy)); sh = sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * op))
    img.paste(Image.new('RGBA', (W, H), rgb + (255,)), (0, 0), sh); img.alpha_composite(item, (x, y))


def crop_alpha(im):
    return im.crop(im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())


def tw(text, f, track):
    return sum(f.getlength(c) for c in text) + track * (len(text) - 1)


def base_text(d, x, base, text, f, fill, track):
    for c in text:
        d.text((x, base), c, font=f, fill=fill, anchor='ls'); x += f.getlength(c) + track


def pair_line(d, cx, base, a, fa, ca, ta, b, fb, cb, tb, gap=30):
    total = tw(a, fa, ta) + gap + tw(b, fb, tb); x = cx - total / 2
    base_text(d, x, base, a, fa, ca, ta); base_text(d, x + tw(a, fa, ta) + gap, base, b, fb, cb, tb)


def check_safe(label, boxes):
    for name, (y0, y1) in boxes.items():
        assert y0 >= SAFE_TOP and y1 <= SAFE_BOT, f'{label}: {name} y {y0}-{y1} leaves the safe zone {SAFE_TOP}-{SAFE_BOT}'


def trim_alpha(im, box):
    a = np.array(im); a[box[1]:box[3], box[0]:box[2], 3] = 0; return Image.fromarray(a)


# ---------------------------------------------------------------- Story 1: New York Night
def story_nyn():
    canvas(arch_top=520, arch_r=470, surf_top=1330, surf_front=1470, base_y=1390)
    s = dict(bg_a=(251, 240, 226), bg_b=(241, 217, 194), niche_rgb=(240, 218, 198), stone=(4, 0, -4))
    img = B.background(s)
    glow(img, 380, 980, 560, 620, (176, 150, 222), 0.16)            # faint blue-violet bloom echoing the gradient glass
    glow(img, 760, 700, 600, 500, (255, 214, 176), 0.20)            # warm peach light from the right
    B.niche(img, s); B.travertine(img, s)

    box = B.load_clean(A + 'nyn_box_hi.png', 720)
    bt = np.array(Image.open(A + 'nyn_bottle_hi.png').convert('RGBA')); lo = bt[-30:, :, :3].astype(int)
    bt[-30:, :, 3][(lo.min(axis=2) > 165) & (lo.max(axis=2) - lo.min(axis=2) < 40)] = 0
    bt[150:236, 0:188, 3] = 0                                                    # photo's soft shadow line beside the cap base (left of the cap only)
    Image.fromarray(bt).save('/tmp/_bottle.png'); bottle = B.load_clean('/tmp/_bottle.png', 520)               # the real bottle, larger than the box's real ratio (it stands in front)
    bw, bh = bottle.size; xw = box.width; ov = 80
    left = 540 - (bw + xw - ov) / 2 - 10; box_cx = left + bw - ov + xw / 2; box_r = left + bw - ov + xw
    B.stage_bottle(img, box, box_cx, B.BASE_Y)
    # ingredients = real pixels from the supplied flat-lay (peach, vanilla, leaves), grounded with alpha-shaped shadows
    p0 = np.array(Image.open(A + 'ing_hi_pods.png').convert('RGBA')); p0[(p0[..., :3].max(axis=2) > 120) | (p0[..., 1].astype(int) > p0[..., 0].astype(int) - 2), 3] = 0
    pods = Image.fromarray(p0); pods = pods.resize((int(pods.width * .248), int(pods.height * .248)), Image.LANCZOS)
    pods = crop_alpha(pods.rotate(-20, expand=True, resample=Image.BICUBIC)); pods.save('/tmp/_pods.png'); pods = B.load_clean('/tmp/_pods.png', 330)
    drop_shadow(img, pods, int(box_r + 100 - pods.width), B.BASE_Y + 14 - pods.height, dx=12, dy=8, blur=7, op=0.30)
    pe = Image.open(A + 'ing_hi_peach.png').convert('RGBA'); a_ = np.array(pe); hh, ww = a_.shape[:2]; yy_, xx_ = np.mgrid[0:hh, 0:ww]; cxp, cyp = ww * 0.50, hh * 0.52
    outside = ((xx_ - cxp) / (ww * 0.49)) ** 2 + ((yy_ - cyp) / (hh * 0.49)) ** 2 > 1.0
    a_[outside & (xx_ < cxp) & (yy_ < cyp), 3] = 0; Image.fromarray(a_).save('/tmp/_peach.png')      # drop the stem fragment outside the fruit outline only
    pe = B.load_clean('/tmp/_peach.png', 232)
    B.stage_bottle(img, pe, box_r + 38, B.BASE_Y + 56)
    lf = Image.open(A + 'ing_hi_leaf_bl.png').convert('RGBA').rotate(12, expand=True, resample=Image.BICUBIC); lf.save('/tmp/_leaf.png'); lf = B.load_clean('/tmp/_leaf.png', 150)
    drop_shadow(img, lf, int(left - 62), B.BASE_Y + 52 - lf.height, dx=10, dy=7, blur=6, op=0.30)
    B.stage_bottle(img, bottle, left + bw / 2, B.BASE_Y)

    d = ImageDraw.Draw(img); brown, gold = (74, 52, 40), (176, 141, 87)
    ind = (66, 54, 118)
    tracked_in(d, 540, 292, 'MAD PARFUMEUR', B.font(INTER_M, 24), brown, 12)
    tf, size = B.fit_width(d, 'NEW YORK NIGHT', CORM, 'SemiBold', 104, 820, track_ratio=.10)
    tracked_in(d, 540, 382, 'NEW YORK NIGHT', tf, ind, size * .10)
    d.line((500, 448, 580, 448), fill=gold, width=2); d.ellipse((536, 444, 544, 452), fill=gold)
    tracked_in(d, 540, 1508, 'Discover the fragrance', B.font(CORM, 50, 'Medium'), brown, 3)
    d.line((500, 1556, 580, 1556), fill=gold, width=2)
    pair_line(d, 540, 1606, 'AVAILABLE AT', B.font(INTER_M, 21), (143, 105, 52), 9, 'SCENTRO', B.font(CORM, 42, 'SemiBold'), brown, 12)
    check_safe('nyn', {'title block': (270, 460), 'bottom block': (1510, 1620)})
    return img


# ---------------------------------------------------------------- Story 2: Golden Soul
def jasmine_light(img, seed, side, rgb=(255, 226, 170), strength=0.10):
    """Soft dappled light cast through a jasmine vine (leaf pairs + five-petal blossoms) onto the wall - never covers the text area."""
    r = np.random.default_rng(seed); m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    def leaf(cx, cy, ang, ln, wd):
        t = np.linspace(0, np.pi, 20); p = [(ln * (k / np.pi - .5), wd * np.sin(k) * .5) for k in t] + [(ln * (k / np.pi - .5), -wd * np.sin(k) * .5) for k in t[::-1]]
        ca, sa = np.cos(ang), np.sin(ang); d.polygon([(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in p], fill=255)
    def blossom(cx, cy, rad):
        for k in range(5):
            a = k * 2 * np.pi / 5 + r.uniform(0, .5); leaf(cx + np.cos(a) * rad * .55, cy + np.sin(a) * rad * .55, a, rad * 1.15, rad * .5)
    x0 = W + 40 if side == 'r' else -40; y0 = 760; x, y, a = x0, y0, (np.pi if side == 'r' else 0.0)
    for i in range(9):
        a += r.normal(0, .07) + (.10 if side == 'r' else -.10); x += np.cos(a) * 70; y += np.sin(a) * 70
        leaf(x, y, a + 1.1, 120, 50); leaf(x, y, a - 1.1, 110, 46)
        if i % 3 == 1: blossom(x + r.uniform(-20, 20), y + r.uniform(-50, 50), 34)
    m = m.filter(ImageFilter.GaussianBlur(11)).point(lambda v: int(v * strength))
    keep = Image.new('L', (W, H), 0); ImageDraw.Draw(keep).rectangle((0, 560, W, 1320), fill=255)         # wall around the product only
    m = Image.fromarray((np.asarray(m, np.float32) * np.asarray(keep, np.float32) / 255).astype(np.uint8))
    img.paste(Image.new('RGBA', (W, H), tuple(rgb) + (255,)), (0, 0), m)


def story_gs():
    canvas(arch_top=520, arch_r=470, surf_top=1330, surf_front=1500, base_y=1410)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = np.clip(yy / H * 0.9 + xx / W * 0.1, 0, 1)[..., None]
    base = np.array([20, 16, 13], np.float32) * (1 - t) + np.array([9, 8, 7], np.float32) * t
    base += rng.normal(0, 0.9, (H, W, 1))
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA')
    glow(img, 540, 960, 760, 860, (150, 108, 50), 0.34)              # warm pool of light behind the product
    glow(img, 300, 560, 520, 480, (255, 222, 160), 0.10)             # key light, upper left
    # arch niche: slightly lifted black, champagne-gold rim
    cx, top, R = 540, B.ARCH_TOP, B.ARCH_R
    m = Image.new('L', (W * 2, H * 2), 0); dm = ImageDraw.Draw(m)
    dm.ellipse(((cx - R) * 2, top * 2, (cx + R) * 2, (top + 2 * R) * 2), fill=255); dm.rectangle(((cx - R) * 2, (top + R) * 2, (cx + R) * 2, B.SURF_TOP * 2), fill=255)
    m = m.resize((W, H), Image.LANCZOS)
    ar = np.asarray(m, np.float32)[..., None] / 255
    yy2, xx2 = np.mgrid[0:H, 0:W].astype(np.float32); lift = np.clip(1 - np.hypot((xx2 - 540) / 520, (yy2 - 1000) / 640), 0, 1)[..., None] ** 1.3
    a = np.asarray(img, np.float32)[..., :3]
    niche_col = np.array([30, 24, 18], np.float32) + lift * np.array([40, 28, 14], np.float32)
    a = a * (1 - ar * 0.92) + niche_col * ar * 0.92
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    dr = ImageDraw.Draw(img, 'RGBA')
    dr.arc((cx - R, top, cx + R, top + 2 * R), 180, 360, fill=(205, 170, 112, 210), width=3)
    dr.line((cx - R, top + R, cx - R, B.SURF_TOP), fill=(205, 170, 112, 210), width=3); dr.line((cx + R, top + R, cx + R, B.SURF_TOP), fill=(205, 170, 112, 210), width=3)
    # polished black stone: lit top surface, shaded front face, champagne edge highlight
    ys0, ys1 = B.SURF_TOP, B.SURF_FRONT; h = H - ys0
    col = np.zeros((h, W, 3), np.float32); top_h = ys1 - ys0
    ty = np.linspace(0, 1, top_h, dtype=np.float32)[:, None, None]
    col[:top_h] = np.array([46, 37, 29], np.float32) * (1 - 0.35 * ty) + np.array([8, 6, 4], np.float32) * ty * 0
    fy = np.linspace(0, 1, h - top_h, dtype=np.float32)[:, None, None]
    col[top_h:] = np.array([17, 14, 11], np.float32) * (1 - 0.6 * fy)
    col += ndi.gaussian_filter(rng.normal(0, 1, (h, W)), (0.8, 60))[..., None] * 3.0 + rng.normal(0, 0.8, (h, W, 1))
    img.paste(Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert('RGBA'), (0, ys0))
    dd = ImageDraw.Draw(img, 'RGBA'); dd.line((0, ys0, W, ys0), fill=(80, 64, 46, 255), width=1); dd.line((0, ys1, W, ys1), fill=(214, 182, 126, 235), width=2)
    glow(img, 540, B.BASE_Y + 10, 520, 120, (205, 160, 88), 0.30)    # gold light pooling on the polished top

    g0 = np.array(Image.open(A + 'golden_soul_group.png').convert('RGBA')); reg = g0[284:343, 370:420]
    mn, mx = reg[..., :3].min(axis=2).astype(int), reg[..., :3].max(axis=2).astype(int)
    reg[(mn > 150) & (mx - mn < 34), 3] = 0; g0[284:343, 370:420] = reg
    for (y0_, y1_, x0_) in ((326, 340, 470), (340, 520, 548)):                 # backdrop strip on the shoulder top / right edge only (keeps the real specular highlights)
        zr = g0[y0_:y1_, x0_:]; mn2, mx2 = zr[..., :3].min(axis=2).astype(int), zr[..., :3].max(axis=2).astype(int)
        zr[(mn2 > 150) & (mx2 - mn2 < 34), 3] = 0; g0[y0_:y1_, x0_:] = zr
    g0[..., 3] = np.array(Image.fromarray(g0[..., 3]).filter(ImageFilter.MinFilter(3)))                # photo backdrop visible between box edge and bottle neck
    Image.fromarray(g0).save('/tmp/_gs_group.png'); grp = B.load_clean('/tmp/_gs_group.png', 820)
    gx, gy = 540 - grp.width // 2, B.BASE_Y - grp.height
    # reflection on the polished surface (only as deep as the top surface is)
    rh = ys1 - B.BASE_Y - 8
    refl = grp.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, grp.width, rh))
    fade = (np.linspace(0.34, 0, rh) ** 1.4)[:, None] * np.ones((1, grp.width))
    ra = Image.fromarray((np.asarray(refl.getchannel('A'), np.float32) * fade).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.4))
    refl = refl.filter(ImageFilter.GaussianBlur(1.4)); refl.putalpha(ra); img.alpha_composite(refl, (gx, B.BASE_Y))
    con = Image.new('L', (W, H), 0); ImageDraw.Draw(con).ellipse((gx + 10, B.BASE_Y - 8, gx + grp.width - 10, B.BASE_Y + 14), fill=230)
    img.paste(Image.new('RGBA', (W, H), (0, 0, 0, 255)), (0, 0), con.filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * .8)))
    img.alpha_composite(grp, (gx, gy))

    d = ImageDraw.Draw(img); champ = (216, 186, 132); ivory = (234, 222, 202); gold = (190, 156, 98)
    tracked_in(d, 540, 292, 'MAD PARFUMEUR', B.font(INTER_M, 24), ivory, 12)
    tf, size = B.fit_width(d, 'GOLDEN SOUL', CORM, 'SemiBold', 108, 860, track_ratio=.12)
    tracked_in(d, 540, 376, 'GOLDEN SOUL', tf, champ, size * .12)
    d.line((500, 436, 580, 436), fill=gold, width=2)
    tracked_in(d, 540, 472, 'EXTRAIT DE PARFUM', B.font(INTER_M, 22), (200, 170, 118), 11)
    d.line((500, 1555, 580, 1555), fill=gold, width=2)
    pair_line(d, 540, 1600, 'AVAILABLE AT', B.font(INTER_M, 21), (198, 168, 116), 9, 'SCENTRO', B.font(CORM, 42, 'SemiBold'), champ, 12)
    check_safe('gs', {'title block': (270, 490), 'bottom block': (1540, 1620)})
    return img


JOBS = {'nyn': (story_nyn, 'stories/output/scentro_new_york_night_story.png'),
        'gs': (story_gs, 'stories/output/scentro_golden_soul_story.png')}

if __name__ == '__main__':
    os.makedirs('stories/output', exist_ok=True)
    for k in (sys.argv[1:] or JOBS):
        fn, out = JOBS[k]; im = fn().convert('RGB'); assert im.size == (W, H); im.save(out, optimize=True); print(out, im.size)
