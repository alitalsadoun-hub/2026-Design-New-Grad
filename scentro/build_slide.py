"""SCENTRO carousel slide builder v2 (editable source).  Usage: python3 build_slide.py N   (N = 1..6)
Layers: background glow -> arch niche (frame + inner shadow) -> travertine surface -> bottle reflections/shadows -> bottles -> type.
Bottles are real photographs (transparent cutouts in assets/cutouts); they are only resized, edge-cleaned and positioned."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as ndi

W, H = 1080, 1350
CORM = 'fonts/CormorantGaramond-VF.ttf'
INTER = '/usr/share/fonts/opentype/inter/Inter-Regular.otf'
INTER_M = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'

# ---- layout constants ------------------------------------------------------------------------------
ARCH_CX, ARCH_TOP, ARCH_R = 540, 452, 372       # arch niche: 168..912 wide
SURF_TOP, SURF_FRONT = 1128, 1214               # polished top surface (back edge .. front edge)
BASE_Y = 1176                                   # bottles stand mid-way on the surface
GAP = 64


def S(title, mad, orig, inspired, title_rgb, bg_a, bg_b, niche_rgb, mad_h=640, orig_h=470, name_size=46, stone=(0, 0, 0), photo=None, out=None):
    P = lambda n: n if '/' in n else f'assets/cutouts/{n}.png'
    return dict(title=title, mad=P(mad), orig=P(orig), inspired=inspired,
                title_rgb=title_rgb, bg_a=bg_a, bg_b=bg_b, niche_rgb=niche_rgb, mad_h=mad_h, orig_h=orig_h,
                name_size=name_size, stone=stone, photo=photo, out=out or f'output/slide{{n}}_{title.lower()}.png')


SLIDES = {
    1: S('ROUGE', 'mad_rouge', 'brx540_extrait', 'Baccarat Rouge 540 Extrait de Parfum', (122, 20, 38), (245, 237, 224), (231, 217, 197), (226, 209, 187), mad_h=610, orig_h=440, name_size=40),
    2: S('TREASURE', 'mad_treasure', 'naxos', 'Naxos', (142, 98, 34), (246, 238, 220), (233, 215, 186), (229, 208, 176), mad_h=600, orig_h=470, stone=(4, 0, -6)),
    3: S('MARJORIE', 'mad_marjorie', 'guidance', 'Guidance', (148, 86, 92), (247, 240, 231), (237, 221, 213), (230, 208, 198), mad_h=610, orig_h=380, stone=(2, -2, -2),),
    4: S('EFFECT', 'mad_effect', 'side_effect', 'Side Effect', (104, 30, 38), (244, 235, 222), (229, 212, 194), (224, 202, 182), mad_h=610, orig_h=450),
    5: S('DREAMLIGHT', 'mad_dreamlight', 'attrape_reves', 'Attrape-Rêves', (126, 88, 130), (248, 242, 240), (236, 225, 232), (230, 214, 222), mad_h=560, orig_h=450, stone=(0, -2, 3)),
    6: S('FORZA', 'mad_forza', 'alexandria_ii', 'Alexandria II', (106, 74, 42), (245, 237, 223), (230, 215, 191), (226, 207, 178), mad_h=500, orig_h=470, stone=(2, 0, -3)),
}
SLIDES[31] = dict(SLIDES[3], photo=dict(src='assets/source/mad_marjorie_original.webp', crop=(245, 105, 595, 630), size=(450, 675)), mad_h=600, orig_h=395, out='output/slide3_marjorie_framed.png')

# ---- collection 2 (new MAD carousel) ----------------------------------------------------------------
C2 = 'assets/cutouts/collection2/'
SLIDES[11] = S('SATEEN OUD', C2 + 'mad_sateen_oud.png', C2 + 'oud_satin_mood.png', 'Oud Satin Mood', (38, 48, 84),
               (244, 237, 226), (229, 217, 199), (224, 211, 192), mad_h=520, orig_h=500, stone=(0, 0, 2),
               out='output/collection2/slide1_sateen_oud.png')

def C2S(n, title, mad, orig, inspired, title_rgb, bg_a, bg_b, niche, mad_h, orig_h, stone=(0, 0, 0), name_size=46):
    slug = title.lower().replace(' ', '_')
    return S(title, C2 + mad + '.png', C2 + orig + '.png', inspired, title_rgb, bg_a, bg_b, niche, mad_h=mad_h, orig_h=orig_h,
             stone=stone, name_size=name_size, out=f'output/collection2/slide{n}_{slug}.png')


SLIDES[12] = C2S(2, 'BRUNO EXOTIC', 'mad_bruno_exotic', 'amyris_homme', 'Amyris Homme', (150, 48, 36), (245, 236, 222), (231, 214, 194), (227, 206, 186), 560, 470, stone=(3, 0, -3))
SLIDES[13] = C2S(3, 'BRUNO DETOX', 'mad_bruno_detox', 'delox', 'Delox', (96, 50, 90), (246, 239, 233), (233, 221, 223), (229, 212, 216), 560, 470, stone=(1, -1, 2))
SLIDES[14] = C2S(4, 'ADRIA', 'mad_adria', 'craquele', 'Craquelé', (24, 84, 88), (244, 239, 229), (227, 225, 211), (222, 220, 205), 560, 480, stone=(-2, 1, 0))
SLIDES[15] = C2S(5, 'INVITING', 'mad_inviting', 'supreme_bouquet', 'Supreme Bouquet', (150, 112, 40), (248, 241, 226), (237, 223, 195), (233, 217, 187), 520, 480, stone=(3, 1, -5))
SLIDES[16] = C2S(6, 'DRACO', 'mad_draco', 'draco', 'Draco', (28, 52, 104), (244, 239, 229), (229, 223, 213), (223, 216, 205), 600, 440, stone=(0, 0, 2))
SLIDES[17] = C2S(7, 'GUMIN', 'mad_gumin', 'gumin', 'Gumin', (20, 96, 118), (244, 240, 230), (227, 227, 215), (221, 223, 211), 540, 470, stone=(-2, 1, 1))
MAXW = 640   # max combined width of both bottles + gap, so they always sit inside the arch

rng = np.random.default_rng(11)


# ---- helpers ---------------------------------------------------------------------------------------
def font(path, size, var=None):
    f = ImageFont.truetype(path, size)
    if var:
        f.set_variation_by_name(var)
    return f


def tracked(draw, cx, cy, text, f, fill, track):
    ws = [draw.textlength(c, font=f) for c in text]
    x = cx - (sum(ws) + track * (len(text) - 1)) / 2
    for c, w in zip(text, ws):
        draw.text((x, cy), c, font=f, fill=fill, anchor='lm')
        x += w + track


def fit_width(draw, text, path, var, start, max_w, track_ratio=0.0, track_px=0.0, min_size=24):
    size = start
    while size > min_size:
        f = font(path, size, var)
        tw = sum(draw.textlength(c, font=f) for c in text) + (track_ratio * size + track_px) * (len(text) - 1)
        if tw <= max_w:
            break
        size -= 2
    return font(path, size, var), size


def noise(h, w, sy, sx, amp):
    n = ndi.gaussian_filter(rng.normal(0, 1, (h, w)).astype(np.float32), (sy, sx))
    return n / (n.std() + 1e-6) * amp


def arr(im):
    return np.asarray(im, dtype=np.float32)


# ---- scene -----------------------------------------------------------------------------------------
def background(s):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = np.clip(xx / W * 0.35 + yy / H * 0.8, 0, 1)[..., None]
    img = np.array(s['bg_a'], np.float32) * (1 - t) + np.array(s['bg_b'], np.float32) * t
    # soft window-light bloom from the upper left + gentle vignette
    d = np.hypot((xx - 180) / 900, (yy - 120) / 700)[..., None]
    img += 9 * np.clip(1 - d, 0, 1) ** 2
    v = np.hypot((xx - W / 2) / (W * .75), (yy - H * .55) / (H * .8))[..., None]
    img *= 1 - 0.07 * np.clip(v - .35, 0, 1)
    img += rng.normal(0, 0.9, (H, W, 1))
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')


def arch_mask(inset=0, ss=3):
    m = Image.new('L', (W * ss, H * ss), 0)
    d = ImageDraw.Draw(m)
    r = ARCH_R - inset
    top = ARCH_TOP + inset
    d.ellipse(((ARCH_CX - r) * ss, top * ss, (ARCH_CX + r) * ss, (top + 2 * r) * ss), fill=255)
    d.rectangle(((ARCH_CX - r) * ss, (top + r) * ss, (ARCH_CX + r) * ss, SURF_TOP * ss), fill=255)
    return m.resize((W, H), Image.LANCZOS)


def niche(img, s):
    outer = arch_mask(0)
    inner = arch_mask(20)
    # frame: slightly lighter than the wall, with a fine highlight on the upper-left edge
    frame_col = np.clip(np.array(s['bg_b'], np.float32) + np.array([6, 5, 3]), 0, 255)
    img.paste(Image.new('RGBA', (W, H), tuple(int(v) for v in frame_col) + (255,)), (0, 0), outer)
    o = arr(outer) / 255
    # soft shadow the frame casts onto the wall (down-right)
    sh = Image.fromarray((np.roll(np.roll(o, 10, 0), 8, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))
    sh_a = np.clip(arr(sh) / 255 - o, 0, 1) * 0.22
    base = arr(img)[..., :3]
    base = base * (1 - sh_a[..., None]) + np.array([120, 95, 70], np.float32) * sh_a[..., None]
    # niche interior: tinted stone, darker toward the edges, with a warm glow behind the bottles
    i = arr(inner) / 255
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    glow = np.clip(1 - np.hypot((xx - ARCH_CX) / 430, (yy - 860) / 520), 0, 1)[..., None] ** 1.4
    col = np.array(s['niche_rgb'], np.float32)[None, None, :] * (0.93 + 0.12 * glow) + 6 * glow
    # inner shadow: light comes from upper-left, so the top/left walls of the niche are in shade
    shifted = np.roll(np.roll(i, 26, 0), 20, 1)
    shifted = ndi.gaussian_filter(shifted, 16)
    ins = np.clip(i - shifted, 0, 1)[..., None] * 0.30
    col = col * (1 - ins) + np.array([110, 85, 62], np.float32) * ins
    col += noise(H, W, 1.2, 1.2, 0.8)[..., None]
    base = base * (1 - i[..., None]) + col * i[..., None]
    out = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA')
    img.paste(out, (0, 0))
    # hairline highlight along the frame's outer edge
    hl = ImageDraw.Draw(img)
    hl.arc((ARCH_CX - ARCH_R, ARCH_TOP, ARCH_CX + ARCH_R, ARCH_TOP + 2 * ARCH_R), 180, 360, fill=(255, 250, 240, 150), width=2)


def travertine(img, s):
    y0, y1 = SURF_TOP, H
    h = y1 - y0
    st = np.array(s['stone'], np.float32)
    # stone body: broad horizontal strata + fine grain
    tone = 0.0 + noise(h, W, 0.8, 90, 5.5) + noise(h, W, 3, 40, 3.5) + noise(h, W, 0.6, 5, 1.5)
    tone2 = np.repeat(ndi.gaussian_filter(rng.normal(0, 1, (h, 1)), 1.6), W, axis=1) * 4
    top_h = SURF_FRONT - y0
    col = np.zeros((h, W, 3), np.float32)
    # top surface: light, brightest at the front edge's far side, slight depth falloff
    ty = np.linspace(0, 1, top_h, dtype=np.float32)[:, None, None]
    col[:top_h] = np.array([232, 220, 200], np.float32) * (0.97 + 0.04 * ty) + st
    # front face: shaded (faces away from the light), darker toward the bottom
    fy = np.linspace(0, 1, h - top_h, dtype=np.float32)[:, None, None]
    col[top_h:] = np.array([200, 185, 164], np.float32) * (1.0 - 0.10 * fy) + st
    col += (tone + tone2)[..., None]
    # pits: small, soft, low contrast, elongated along the strata (not white speckle)
    pits = np.zeros((h, W), np.float32)
    for _ in range(260):
        x, y = rng.integers(0, W), rng.integers(0, h)
        ln, th = rng.integers(6, 34), rng.integers(1, 3)
        pits[y:y + th, x:x + ln] = rng.uniform(0.5, 1.0)
    pits = ndi.gaussian_filter(pits, 0.8)
    col -= pits[..., None] * np.array([26, 28, 32], np.float32)
    col += ndi.shift(pits, (1, 0), order=1)[..., None] * 7  # tiny lit lower lip
    im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert('RGBA')
    img.paste(im, (0, y0))
    d = ImageDraw.Draw(img)
    d.line((0, y0, W, y0), fill=(205, 190, 168, 255), width=1)                    # where wall meets surface
    d.line((0, SURF_FRONT, W, SURF_FRONT), fill=(248, 241, 228, 255), width=2)   # lit front edge
    d.line((0, SURF_FRONT + 2, W, SURF_FRONT + 2), fill=(170, 154, 132, 120), width=2)
    # soft shadow the surface edge throws down the front face
    edge = np.zeros((H, W), np.float32)
    edge[SURF_FRONT + 3:SURF_FRONT + 30, :] = np.linspace(1, 0, 27)[:, None]
    a = arr(img)[..., :3]
    a = a * (1 - 0.16 * edge[..., None]) + 0
    img.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'), (0, 0))


# ---- bottles ---------------------------------------------------------------------------------------
def load_clean(path, height):
    """Load cutout, remove edge halo (colour decontamination), resize with premultiplied alpha, light sharpen."""
    im = Image.open(path).convert('RGBA')
    a = np.array(im)
    al = a[..., 3].astype(np.float32) / 255
    solid = al > 0.97
    idx = ndi.distance_transform_edt(~solid, return_distances=False, return_indices=True)
    rgb = a[..., :3][idx[0], idx[1]]
    edge = al < 0.97
    a[..., :3][edge] = rgb[edge]
    a[..., 3] = (np.clip((al - 0.12) / 0.82, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(a)
    w = round(im.width * height / im.height)
    scale = height / im.height
    if scale > 1.05:   # upscale in two steps, then recover crispness
        mid = im.resize((round(im.width * (1 + scale) / 2), round(im.height * (1 + scale) / 2)), Image.LANCZOS)
        im = mid.resize((w, height), Image.LANCZOS)
        rgb_img = im.convert('RGB').filter(ImageFilter.UnsharpMask(1.4, 55, 2))
    else:
        im = im.resize((w, height), Image.LANCZOS)
        rgb_img = im.convert('RGB').filter(ImageFilter.UnsharpMask(0.8, 35, 2))
    out = rgb_img.convert('RGBA')
    out.putalpha(im.getchannel('A'))
    return out


def stage_bottle(img, b, cx, base_y):
    w, h = b.size
    x, y = round(cx - w / 2), base_y - h
    al = b.getchannel('A')
    # 1) wide, soft ambient occlusion on the surface
    amb = Image.new('L', (W, H), 0)
    ImageDraw.Draw(amb).ellipse((x - 14, base_y - 15, x + w + 30, base_y + 20), fill=120)
    amb = amb.filter(ImageFilter.GaussianBlur(14))
    # 2) cast shadow, light from upper-left -> falls to the right
    cast = Image.new('L', (W, H), 0)
    ImageDraw.Draw(cast).polygon([(x + w * .1, base_y - 4), (x + w * .9, base_y - 4),
                                  (x + w * 1.55, base_y + 16), (x + w * .75, base_y + 16)], fill=150)
    cast = cast.filter(ImageFilter.GaussianBlur(10))
    # 3) tight contact shadow
    con = Image.new('L', (W, H), 0)
    ImageDraw.Draw(con).ellipse((x + 3, base_y - 5, x + w - 3, base_y + 6), fill=235)
    con = con.filter(ImageFilter.GaussianBlur(3.2))
    dark = Image.new('RGBA', (W, H), (70, 52, 38, 255))
    for m, k in ((amb, .42), (cast, .34), (con, .78)):
        img.paste(dark, (0, 0), m.point(lambda v, k=k: int(v * k)))
    # 4) glossy-surface reflection: mirrored bottle fading out within ~34px of the base
    rh = 34
    refl = b.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, w, rh))
    fade = Image.fromarray((np.linspace(0.30, 0, rh)[:, None] * np.ones((1, w)) * 255).astype(np.uint8))
    ra = Image.fromarray((arr(refl.getchannel('A')) * arr(fade) / 255).astype(np.uint8))
    refl = refl.filter(ImageFilter.GaussianBlur(0.9))
    refl.putalpha(ra.filter(ImageFilter.GaussianBlur(0.9)))
    img.alpha_composite(refl, (x, base_y))
    # 5) the bottle itself
    img.alpha_composite(b, (x, y))


def photo_panel(s):
    """Marjorie: the original lifestyle photo (bottle intact with its roses/peaches) in a standing arch-shaped stone frame."""
    p = s['photo']; w, h = p['size']; fr = 18
    ph = Image.open(p['src']).convert('RGB').crop(p['crop'])
    ph = ph.resize((w, h), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 45, 2))
    ss = 3
    def arch_m(wm, hm):
        m = Image.new('L', (wm * ss, hm * ss), 0); d = ImageDraw.Draw(m)
        d.ellipse((0, 0, wm * ss - 1, wm * ss - 1), fill=255); d.rectangle((0, wm * ss // 2, wm * ss - 1, hm * ss - 1), fill=255)
        return m.resize((wm, hm), Image.LANCZOS)
    W2, H2 = w + 2 * fr, h + fr
    panel = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    frame_col = tuple(int(v) for v in np.clip(np.array(s['bg_b'], np.float32) + np.array([12, 11, 9]), 0, 255))
    panel.paste(Image.new('RGBA', (W2, H2), frame_col + (255,)), (0, 0), arch_m(W2, H2))
    inner = Image.new('RGBA', (w, h)); inner.paste(ph.convert('RGBA'), (0, 0))
    m_in = arch_m(w, h)
    # subtle inner shade so the photo sits inside the frame
    sh = np.roll(np.roll(arr(m_in) / 255, 10, 0), 8, 1); sh = ndi.gaussian_filter(sh, 8)
    ins = np.clip(arr(m_in) / 255 - sh, 0, 1)[..., None] * 0.28
    a = arr(inner)[..., :3] * (1 - ins) + np.array([100, 80, 60], np.float32) * ins
    inner = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'); inner.putalpha(m_in)
    panel.alpha_composite(inner, (fr, fr))
    return panel


# ---- build -----------------------------------------------------------------------------------------
def build(n):
    s = SLIDES[n]
    s = dict(s); s['out'] = s['out'].format(n=n)
    img = background(s)
    if not s['photo']:
        niche(img, s)
    travertine(img, s)

    d = ImageDraw.Draw(img)
    brown, gold = (74, 52, 40), (176, 141, 87)
    # header (logo placeholder until the real file arrives)
    tracked(d, 540, 78, 'SCENTRO', font(CORM, 42, 'Medium'), brown, 20)
    d.line((517, 126, 563, 126), fill=gold, width=2)
    # title block (tightened so the bottles can be larger)
    tf, size = fit_width(d, s['title'], CORM, 'SemiBold', 100, 720, track_ratio=.12)
    tracked(d, 540, 200, s['title'], tf, s['title_rgb'], size * .12)
    tracked(d, 540, 281, 'MAD PARFUMEUR', font(INTER, 19), brown, 9)
    d.line((480, 311, 600, 311), fill=gold, width=2)
    d.ellipse((536, 307, 544, 315), fill=gold)
    tracked(d, 540, 340, 'INSPIRED BY', font(INTER_M, 16), (143, 105, 52), 8)
    nf, _ = fit_width(d, s['inspired'], CORM, 'SemiBold', s['name_size'], 700, track_px=1.5)
    tracked(d, 540, 388, s['inspired'], nf, brown, 1.5)

    # bottles: MAD hero on the left, original on the right, shared baseline, group centred on the arch
    b1 = photo_panel(s) if s['photo'] else load_clean(s['mad'], s['mad_h'])
    b2 = load_clean(s['orig'], s['orig_h'])
    if not s['photo'] and b1.width + GAP + b2.width > MAXW:   # keep both bottles inside the arch
        f = (MAXW - GAP) / (b1.width + b2.width)
        b1 = load_clean(s['mad'], round(s['mad_h'] * f)); b2 = load_clean(s['orig'], round(s['orig_h'] * f))
    left = ARCH_CX - (b1.width + GAP + b2.width) / 2
    stage_bottle(img, b1, left + b1.width / 2, BASE_Y)
    stage_bottle(img, b2, left + b1.width + GAP + b2.width / 2, BASE_Y)

    out = img.convert('RGB')
    import os; os.makedirs(os.path.dirname(s['out']), exist_ok=True)
    out.save(s['out'], optimize=True)
    print(s['out'], out.size)


if __name__ == '__main__':
    for a in sys.argv[1:]:
        build(int(a))
