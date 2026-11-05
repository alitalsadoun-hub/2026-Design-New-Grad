"""SCENTRO women's collection (MAD Selective 100 ml) - reuses the scene/bottle system from build_slide.py.
Usage: python3 build_women.py A113 [...]   MAD hero bottle + smaller inspired-by original, official notes in place of the title tagline."""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import build_slide as B

C = 'collection3/assets/cutouts/'
def W(mad, orig, notes, title_rgb, bg_a, bg_b, niche, stone=(0, 0, 0), mad_h=640, orig_h=450, gobo=1):
    return dict(cut=C + mad + '.png', orig=C + orig + '.png', notes=notes, title_rgb=title_rgb, bg_a=bg_a, bg_b=bg_b,
                niche_rgb=niche, stone=stone, hero_h=mad_h, orig_h=orig_h, gobo=gobo)

W_ITEMS = {
 'A113': W('a113', 'orig_alien_goddess', 'Bergamot  ·  Jasmine  ·  Vanilla  ·  Cashmere', (168, 104, 70), (247, 240, 229), (237, 222, 203), (233, 214, 194), (3, 0, -3), 640, 470, 1),
 'A118': W('a118', 'orig_armani_my_way', 'Bergamot  ·  Jasmine  ·  Valley Lily  ·  Caramel', (156, 92, 98), (248, 240, 236), (238, 222, 217), (233, 213, 208), (2, -2, -1), 640, 430, 2),
 'B103': W('b103', 'orig_burberry_her_edp', 'Raspberry  ·  Blackberry  ·  Violet  ·  Vanilla', (112, 86, 150), (244, 240, 246), (229, 222, 238), (223, 214, 234), (-1, -1, 3), 640, 440, 3),
 'B105': W('b105', 'orig_burberry_her_elixir', 'Strawberry  ·  Blackberry  ·  Jasmine  ·  Vanilla', (140, 82, 120), (247, 240, 241), (236, 223, 231), (231, 214, 225), (2, -1, 1), 640, 460, 1),
 'B107': W('b107', 'orig_burberry_goddess', 'Bergamot  ·  Lavender  ·  Chocolate  ·  Vanilla', (128, 86, 52), (247, 239, 224), (233, 217, 192), (227, 208, 178), (3, 1, -4), 640, 410, 2),
 'D116': W('d116', 'orig_dg_q_edp', 'Sicilian Lemon  ·  Cherry  ·  Jasmine  ·  Cedarwood', (98, 114, 82), (245, 243, 233), (230, 230, 212), (222, 224, 204), (-1, 1, -1), 640, 540, 3),
 'G102': W('g102', 'orig_gucci_guilty_elixir_femme', 'Bitter Almond  ·  Peony  ·  Tonka Bean  ·  Vanilla', (118, 66, 108), (248, 241, 233), (236, 223, 213), (231, 213, 204), (1, -1, 0), 640, 285, 2),
 'K102': W('k102', 'orig_kayali_vanilla_candy_rock_sugar_42', 'Candied Pear · Bubble Gum · Vanilla Cream · Rock Sugar', (176, 88, 118), (251, 242, 244), (243, 225, 230), (238, 215, 222), (3, -2, 1), 640, 460, 1),
 'W213': W('w213', 'orig_ysl_black_opium', 'Pear  ·  Coffee  ·  Jasmine  ·  Vanilla', (92, 64, 44), (247, 241, 229), (233, 221, 201), (226, 211, 189), (2, 0, -3), 640, 390, 3),
 'Y104': W('y104', 'orig_ysl_black_opium_over_red', 'Cherry  ·  Jasmine  ·  Green Tea  ·  Vanilla', (140, 40, 58), (249, 240, 236), (240, 220, 216), (235, 211, 209), (3, -1, -1), 640, 340, 2),
}

def leaf_shadow(img, variant, rgb):
    """Very soft, low-contrast botanical shadow cast on the wall (light from the upper left): a branch with leaves + a few petals."""
    Wd, Hd = img.size; rng = np.random.default_rng(100 + variant)
    m = Image.new('L', (Wd, Hd), 0); d = ImageDraw.Draw(m)
    def leaf(cx, cy, ang, ln, wd):
        t = np.linspace(0, np.pi, 24); pts = []
        for k in t: pts.append((ln * (k / np.pi - .5), wd * np.sin(k) * .5))
        for k in t[::-1]: pts.append((ln * (k / np.pi - .5), -wd * np.sin(k) * .5))
        ca, sa = np.cos(ang), np.sin(ang); d.polygon([(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts], fill=255)
    side = 1 if variant % 2 else -1                      # alternate right / left entry for variety across the carousel
    x0 = Wd + 20 if side == 1 else -20; y0 = [470, 560, 640][variant - 1]
    px, py, ang = x0, y0, np.pi if side == 1 else 0
    for i in range(7):
        ang += (rng.normal(0, .08) + (.12 if side == 1 else -.12)); step = 62
        px += np.cos(ang) * step; py += np.sin(ang) * step
        leaf(px, py, ang + side * 1.0, 118, 46); leaf(px, py, ang - side * 1.0, 104, 40)
    for _ in range(4):
        leaf(x0 - side * rng.uniform(80, 330), y0 + rng.uniform(-90, 190), rng.uniform(0, 6.28), 54, 30)
    m = m.filter(ImageFilter.GaussianBlur(15)).point(lambda v: int(v * 0.11))
    wall = Image.new('L', (Wd, Hd), 0); ImageDraw.Draw(wall).rectangle((0, 150, Wd, B.SURF_TOP), fill=255)   # keep clear of the header and stone
    m = Image.fromarray((np.asarray(m, np.float32) * np.asarray(wall, np.float32) / 255).astype(np.uint8))
    img.paste(Image.new('RGBA', (Wd, Hd), tuple(int(v * .45) for v in rgb) + (255,)), (0, 0), m)

def build(code):
    w = W_ITEMS[code]
    s = dict(bg_a=w['bg_a'], bg_b=w['bg_b'], niche_rgb=w['niche_rgb'], stone=w['stone'])
    img = B.background(s); leaf_shadow(img, w['gobo'], w['bg_b']); B.niche(img, s); B.travertine(img, s)
    d = ImageDraw.Draw(img); brown, gold = (74, 52, 40), (176, 141, 87)
    B.tracked(d, 540, 78, 'SCENTRO', B.font(B.CORM, 42, 'Medium'), brown, 20)
    d.line((517, 126, 563, 126), fill=gold, width=2)
    tf, size = B.fit_width(d, code, B.CORM, 'SemiBold', 104, 720, track_ratio=.12)
    B.tracked(d, 540, 200, code, tf, w['title_rgb'], size * .12)
    B.tracked(d, 540, 281, 'MAD PARFUMEUR', B.font(B.INTER, 19), brown, 9)
    d.line((480, 311, 600, 311), fill=gold, width=2); d.ellipse((536, 307, 544, 315), fill=gold)
    B.tracked(d, 540, 340, 'SELECTIVE  ·  FOR WOMEN', B.font(B.INTER_M, 16), (143, 105, 52), 7)
    nf, _ = B.fit_width(d, w['notes'], B.CORM, 'SemiBold', 38, 800, track_px=1.5)
    B.tracked(d, 540, 388, w['notes'], nf, brown, 1.5)
    b = B.load_clean(w['cut'], w['hero_h']); o = B.load_clean(w['orig'], w['orig_h'])
    left = B.ARCH_CX - (b.width + B.GAP + o.width) / 2
    B.stage_bottle(img, b, left + b.width / 2, B.BASE_Y); B.stage_bottle(img, o, left + b.width + B.GAP + o.width / 2, B.BASE_Y)
    os.makedirs('collection3/output', exist_ok=True); out = f'collection3/output/{code.lower()}.png'
    img.convert('RGB').save(out, optimize=True); print(out)

if __name__ == '__main__':
    for c in (sys.argv[1:] or W_ITEMS): build(c)
