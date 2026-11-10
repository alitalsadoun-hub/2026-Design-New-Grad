"""Extract ingredient cutouts from the supplied New York Night flat-lay (real pixels, colour-keyed masks).
Usage: python3 extract_ingredients.py flat_nobottle.png outdir"""
import sys, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
src, out = sys.argv[1], sys.argv[2]; K = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0     # K = source width / 828 (rects below are in 828-px coordinates)
rgb = np.array(Image.open(src).convert('RGB')); hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
H, S, V = hsv[..., 0] * 2, hsv[..., 1] / 255, hsv[..., 2] / 255            # H in degrees
green = (H > 55) & (H < 110) & (S > 0.28) & (V > 0.25)
white = (S < 0.13) & (V > 0.80)                                              # lily bells / highlights
dark = (V < 0.42)                                                            # vanilla pods / stems' shadows
def cut(name, rect, key, keep=1, grow=2, ellipse=False, minsize=60):
    x0, y0, x1, y1 = [int(round(v * K)) for v in rect]; m = np.zeros(key.shape, bool); it = lambda n: max(1, int(round(n * K))); m[y0:y1, x0:x1] = key[y0:y1, x0:x1]
    if ellipse:
        yy, xx = np.mgrid[0:m.shape[0], 0:m.shape[1]]; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        m &= ((xx - cx) / ((x1 - x0) / 2)) ** 2 + ((yy - cy) / ((y1 - y0) / 2)) ** 2 <= 1.0
    m = ndi.binary_closing(m, iterations=it(3)); m = ndi.binary_fill_holes(m)
    lab, n = ndi.label(m)
    if n == 0: print(name, 'EMPTY'); return
    sz = ndi.sum(m, lab, range(1, n + 1)); order = np.argsort(sz)[::-1]
    mm = np.zeros_like(m)
    for k in order[:keep]:
        if sz[k] >= minsize * K * K: mm |= lab == k + 1
    mm = ndi.binary_opening(mm, iterations=it(1)); mm = ndi.binary_dilation(mm, iterations=it(grow)) if grow else mm
    a = cv2.GaussianBlur(mm.astype(np.float32), (0, 0), 0.9 * K); a = np.clip((a - .2) / .6, 0, 1)
    ys, xs = np.where(a > .02); rgba = np.dstack([rgb, (a * 255).astype(np.uint8)])
    Image.fromarray(rgba).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(f'{out}/{name}.png'); print(name, xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)
# peach: its own colour (pink/orange, more saturated than the backdrop) intersected with an ellipse
pk = (S > 0.40) | (H < 18) & (S > 0.30)
cut('peach', (518, 248, 745, 468), (pk | (H > 40) & (H < 62) & (S > 0.5)) & (V > 0.62), ellipse=True, grow=0)
cut('lily_r', (530, 440, 750, 575), green | white, keep=3)
cut('lily_l', (190, 232, 312, 440), green | white, keep=3)
cut('leaf_bl', (95, 470, 300, 635), green, keep=2)
cut('leaf_br', (435, 600, 580, 675), green)
cut('pods', (55, 335, 530, 735), dark, keep=2, grow=1)
