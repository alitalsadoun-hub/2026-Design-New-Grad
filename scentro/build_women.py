"""SCENTRO women's collection (MAD Selective 100 ml) - reuses the scene/bottle system from build_slide.py.
Usage: python3 build_women.py A113 [...]   Single hero bottle, official notes from scentrojo.com in place of INSPIRED BY."""
import sys, os
from PIL import Image, ImageDraw
import build_slide as B

W_ITEMS = {
    'A113': dict(cut='collection3/assets/cutouts/a113.png', title_rgb=(168, 104, 70), bg_a=(247, 240, 229), bg_b=(237, 222, 203),
                 niche_rgb=(233, 214, 194), stone=(3, 0, -3), notes='Bergamot  ·  Jasmine  ·  Vanilla  ·  Cashmere', hero_h=660),
}

def build(code):
    w = W_ITEMS[code]
    s = dict(bg_a=w['bg_a'], bg_b=w['bg_b'], niche_rgb=w['niche_rgb'], stone=w['stone'])
    img = B.background(s); B.niche(img, s); B.travertine(img, s)
    d = ImageDraw.Draw(img); brown, gold = (74, 52, 40), (176, 141, 87)
    B.tracked(d, 540, 78, 'SCENTRO', B.font(B.CORM, 42, 'Medium'), brown, 20)
    d.line((517, 126, 563, 126), fill=gold, width=2)
    tf, size = B.fit_width(d, code, B.CORM, 'SemiBold', 104, 720, track_ratio=.12)
    B.tracked(d, 540, 200, code, tf, w['title_rgb'], size * .12)
    B.tracked(d, 540, 281, 'MAD PARFUMEUR', B.font(B.INTER, 19), brown, 9)
    d.line((480, 311, 600, 311), fill=gold, width=2); d.ellipse((536, 307, 544, 315), fill=gold)
    B.tracked(d, 540, 340, 'SELECTIVE  ·  FOR WOMEN', B.font(B.INTER_M, 16), (143, 105, 52), 7)
    nf, _ = B.fit_width(d, w['notes'], B.CORM, 'SemiBold', 38, 760, track_px=1.5)
    B.tracked(d, 540, 388, w['notes'], nf, brown, 1.5)
    b = B.load_clean(w['cut'], w['hero_h'])
    B.stage_bottle(img, b, B.ARCH_CX, B.BASE_Y)
    os.makedirs('collection3/output', exist_ok=True); out = f'collection3/output/{code.lower()}.png'
    img.convert('RGB').save(out, optimize=True); print(out)

if __name__ == '__main__':
    for c in sys.argv[1:]: build(c)
