"""SCENTRO men's Selective carousel (MAD Selective 100 ml) - same scene/layout as build_women.py.
Usage: python3 build_men.py [CODE ...]   MAD hero bottle + the original it is inspired by (cut from the MAD Selective catalogue) + 'INSPIRED BY' line.
Notes line = the original's key notes (MAD catalogue). Unisex perfumes are labelled UNISEX."""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import build_slide as B
from build_women import leaf_shadow

C = 'collection4/assets/cutouts/'
def M(mad, orig, label, name, house, notes, title_rgb, bg_a, bg_b, niche, stone=(0, 0, 0), mad_h=640, orig_h=450, gobo=1):
    return dict(cut=C + mad + '.png', orig=C + orig + '.png', label=label, name=name, house=house, notes=notes, title_rgb=title_rgb,
                bg_a=bg_a, bg_b=bg_b, niche_rgb=niche, stone=stone, hero_h=mad_h, orig_h=orig_h, gobo=gobo)

# order = order in the carousel
M_ITEMS = {
 'Y102': M('y102', 'orig_ysl_myslf', 'FOR MEN', 'MYSLF', 'Yves Saint Laurent', 'Bergamot  ·  Patchouli  ·  Orange Blossom', (52, 72, 98), (240, 243, 246), (224, 230, 237), (215, 223, 233), (-2, 0, 3), 640, 500, 1),
 'W129': M('w129', 'orig_pr_1_million_elixir', 'FOR MEN', '1 Million Elixir', 'Paco Rabanne', 'Apple  ·  Vanilla  ·  Patchouli', (150, 108, 36), (248, 242, 226), (237, 223, 190), (230, 212, 176), (3, 1, -5), 640, 440, 2),
 'P102': M('p102', 'orig_pr_1_million_lucky', 'FOR MEN', '1 Million Lucky', 'Paco Rabanne', 'Honey  ·  Hazelnut  ·  Plum', (104, 98, 92), (246, 244, 240), (232, 228, 222), (224, 220, 213), (0, 0, 0), 640, 440, 3),
 'J108': M('j108', 'orig_jpg_le_male_elixir', 'FOR MEN', 'Le Male Elixir', 'Jean Paul Gaultier', 'Cinnamon  ·  Bergamot  ·  Honey', (142, 90, 44), (248, 239, 225), (236, 217, 190), (229, 205, 174), (3, 1, -4), 640, 520, 1),
 'A115': M('a115', 'orig_armani_swy_intensely', 'FOR MEN', 'Stronger With You Intensely', 'Giorgio Armani', 'Vanilla  ·  Cinnamon  ·  Chestnut', (150, 68, 38), (249, 239, 231), (239, 219, 205), (231, 207, 191), (3, -1, -2), 640, 350, 2),
 'J101': M('j101', 'orig_jpg_scandal_pour_homme', 'FOR MEN', 'Scandal Pour Homme', 'Jean Paul Gaultier', 'Caramel  ·  Clary Sage  ·  Tonka Bean', (44, 66, 112), (240, 243, 249), (223, 230, 241), (214, 223, 238), (-2, 0, 4), 640, 410, 3),
 'Q106': M('q106', 'orig_tf_vanille_fatale', 'UNISEX', 'Vanille Fatale', 'Tom Ford', 'Coffee Absolute  ·  Wood  ·  Vanilla Resinoid', (96, 62, 44), (247, 239, 231), (234, 218, 204), (226, 207, 191), (3, 0, -3), 640, 340, 1),
 'Q110': M('q110', 'orig_tf_ombre_leather', 'UNISEX', 'Ombré Leather', 'Tom Ford', 'Saffron  ·  Black Leather  ·  Cardamom', (74, 62, 54), (244, 241, 238), (228, 223, 217), (219, 213, 206), (1, 0, -2), 640, 450, 2),
 'W171': M('w171', 'orig_vr_spicebomb', 'FOR MEN', 'Spicebomb', 'Viktor&Rolf', 'Cinnamon  ·  Leather  ·  Chili', (158, 62, 38), (249, 238, 229), (239, 216, 198), (231, 204, 184), (3, -1, -2), 640, 420, 3),
 'P101': M('p101', 'orig_pdm_pegasus', 'FOR MEN', 'Pegasus', 'Parfums de Marly', 'Bitter Almond  ·  Bergamot  ·  Amber', (112, 104, 124), (246, 245, 244), (231, 229, 228), (222, 220, 220), (0, 0, 1), 640, 470, 1),
}

def build(code):
    w = M_ITEMS[code]
    s = dict(bg_a=w['bg_a'], bg_b=w['bg_b'], niche_rgb=w['niche_rgb'], stone=w['stone'])
    img = B.background(s); leaf_shadow(img, w['gobo'], w['bg_b']); B.niche(img, s); B.travertine(img, s)
    d = ImageDraw.Draw(img); brown, gold = (74, 52, 40), (176, 141, 87)
    B.tracked(d, 540, 78, 'SCENTRO', B.font(B.CORM, 42, 'Medium'), brown, 20)
    d.line((517, 126, 563, 126), fill=gold, width=2)
    tf, size = B.fit_width(d, code, B.CORM, 'SemiBold', 104, 720, track_ratio=.12)
    B.tracked(d, 540, 200, code, tf, w['title_rgb'], size * .12)
    B.tracked(d, 540, 281, 'MAD PARFUMEUR', B.font(B.INTER, 19), brown, 9)
    d.line((480, 311, 600, 311), fill=gold, width=2); d.ellipse((536, 307, 544, 315), fill=gold)
    B.tracked(d, 540, 340, 'SELECTIVE  ·  ' + w['label'], B.font(B.INTER_M, 16), (143, 105, 52), 7)
    nf, _ = B.fit_width(d, w['notes'], B.CORM, 'SemiBold', 38, 800, track_px=1.5)
    B.tracked(d, 540, 388, w['notes'], nf, brown, 1.5)
    b = B.load_clean(w['cut'], w['hero_h']); o = B.load_clean(w['orig'], w['orig_h'])
    left = B.ARCH_CX - (b.width + B.GAP + o.width) / 2
    B.stage_bottle(img, b, left + b.width / 2, B.BASE_Y); B.stage_bottle(img, o, left + b.width + B.GAP + o.width / 2, B.BASE_Y)
    # inspired-by line on the stone front
    d = ImageDraw.Draw(img)
    B.tracked(d, 540, 1262, 'INSPIRED BY', B.font(B.INTER_M, 16), (143, 105, 52), 7)
    line = w['name'] + '   ·   ' + w['house']
    lf, _ = B.fit_width(d, line, B.CORM, 'SemiBold', 40, 900, track_px=1.2)
    B.tracked(d, 540, 1305, line, lf, brown, 1.2)
    os.makedirs('collection4/output', exist_ok=True); out = f'collection4/output/{list(M_ITEMS).index(code) + 1:02d}_{code.lower()}.png'
    img.convert('RGB').save(out, optimize=True); print(out)

if __name__ == '__main__':
    for c in (sys.argv[1:] or M_ITEMS): build(c)
