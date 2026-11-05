"""Extend each approved 1080x1350 (4:5) slide to a 1080x1920 (9:16) plate. Original pixels are untouched and centred;
the wall gradient is extrapolated upward and the stone front face is mirror-continued downward. Usage: make_plates.py"""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
CODES = ['a113', 'a118', 'b103', 'b105', 'b107', 'd116', 'g102', 'k102', 'w213', 'y104']
TOP, BOT = 285, 285          # content block lands at y 285..1635; header ~y 363, bottle bases ~y 1461 (inside Reels safe zone)
rng = np.random.default_rng(5)
def plate(code):
    im = np.asarray(Image.open(f'../collection3/output/{code}.png').convert('RGB'), np.float32); h, w, _ = im.shape
    # --- top: per-column linear extrapolation of the (smoothed) wall gradient, with matching grain
    base = ndi.gaussian_filter(im[:60], (6, 14, 0))
    r0, r1 = base[0:6].mean(0), base[40:46].mean(0); slope = (r0 - r1) / 42.0           # change per px going upward
    ys = np.arange(1, TOP + 1, dtype=np.float32)[::-1][:, None, None]                    # distance above row 0, top-down
    top = r0[None] + slope[None] * ys * np.linspace(1.0, 0.35, TOP)[:, None, None]       # gently flatten the gradient as it extends
    top += rng.normal(0, 0.9, top.shape)
    # --- bottom: mirror the stone front face, darken slightly toward the bottom edge
    face = im[h - 120:]; bot = np.concatenate([face[::-1], face, face[::-1]], 0)[:BOT]
    bot = bot * np.linspace(0.995, 0.93, BOT)[:, None, None]
    out = np.concatenate([top, im, bot], 0)
    # soften the two seams a few px so no line is detectable
    for y in (TOP, TOP + h):
        out[y - 3:y + 3] = ndi.gaussian_filter(out[y - 8:y + 8], (1.6, 0, 0))[5:11]
    out[TOP + 4:TOP + h - 4] = im[4:-4]                                                  # restore original pixels exactly
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(f'plate_{code}.png')
if __name__ == '__main__':
    for c in CODES: plate(c); print(c)
