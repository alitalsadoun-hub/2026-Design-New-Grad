"""Turns a real campaign photo (about 5:6) into a 9:16 Story (1080x1920) WITHOUT cropping the product or inventing pixels:
the photo keeps its full width, and the extra height above / below is the photo's own top / bottom edge, stretched and softly blurred so the colours continue seamlessly.
The photo sits inside the Story safe zone (nothing important above y=250 or below y=1620).
Usage (from scentro/):  python3 stories/build_photo_story.py   ->  stories/output/scentro_story_<name>.png"""
import os, sys
import numpy as np
from PIL import Image, ImageFilter

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 1080, 1920
JOBS = {'rouge': ('stories/assets/photos/mad_rouge_flatlay.jpg', 'stretch', None), 'divine_tough': ('stories/assets/photos/mad_divine_tough_pears.jpg', 'reflect', 1680)}


def story(src, mode='stretch', target_h=None, dy=0, strip=26, blur=46, feather=100):
    ph = Image.open(src).convert('RGB')
    if target_h:                # slightly larger than fit-width: scale to target_h and trim a little from the sides (less to extend above / below)
        sc = target_h / ph.height; ph = ph.resize((round(ph.width * sc), target_h), Image.LANCZOS); x0 = (ph.width - W) // 2; ph = ph.crop((x0, 0, x0 + W, target_h)); h = target_h
    else:
        h = round(ph.height * W / ph.width); ph = ph.resize((W, h), Image.LANCZOS)
    top, bot = (H - h) // 2 + dy, (H - h) // 2 + dy + h                                   # photo occupies y = top .. bot
    # extension = the photo's own edge strip, stretched to the missing height and blurred (colours continue exactly from the photo)
    if mode == 'reflect':       # busy photo (fruit): mirror the photo's own edge and blur it into soft out-of-focus background
        eu, ed = top + feather, H - bot + feather
        feather_blur = 26
        up = ph.crop((0, 0, W, eu)).transpose(Image.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(26))
        dn = ph.crop((0, h - ed, W, h)).transpose(Image.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(26))
    else:                       # calm photo (plain stone): stretch the edge strip
        up = ph.crop((0, 0, W, strip)).resize((W, top + feather), Image.BICUBIC).filter(ImageFilter.GaussianBlur(blur))
        dn = ph.crop((0, h - strip, W, h)).resize((W, H - bot + feather), Image.BICUBIC).filter(ImageFilter.GaussianBlur(blur))
    canvas = Image.new('RGB', (W, H)); canvas.paste(up, (0, 0)); canvas.paste(dn, (0, bot - feather))
    # feather the photo into the extension so there is no visible seam
    m = np.ones((h, W), np.float32); ramp = np.linspace(0, 1, feather, dtype=np.float32)[:, None]
    m[:feather] *= ramp; m[-feather:] *= ramp[::-1]
    mask = Image.fromarray((m * 255).astype(np.uint8)); canvas.paste(ph, (0, top), mask)
    # fine grain so the stretched areas do not band
    a = np.asarray(canvas).astype(np.float32); rng = np.random.default_rng(7); a += rng.normal(0, 1.6, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), (top, bot)


if __name__ == '__main__':
    os.makedirs('stories/output', exist_ok=True)
    for k in (sys.argv[1:] or JOBS):
        im, (t, b) = story(JOBS[k][0], JOBS[k][1], JOBS[k][2]); p = f'stories/output/scentro_story_{k}.png'; im.save(p, optimize=True); print(p, im.size, 'photo y', t, '-', b)
