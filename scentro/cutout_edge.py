"""Edge-based cutout for bottles on plain backgrounds with soft cast shadows: sharp edges outline the bottle, soft shadows are ignored.
Usage: cutout_edge.py in out lo hi [close_iter]"""
import sys, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
src, dst = sys.argv[1], sys.argv[2]; lo, hi = int(sys.argv[3]), int(sys.argv[4]); ci = int(sys.argv[5]) if len(sys.argv) > 5 else 9
im = np.array(Image.open(src).convert('RGB')); g = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
g = cv2.GaussianBlur(g, (0, 0), 1.2)
e = cv2.Canny(g, lo, hi) > 0
e = ndi.binary_dilation(e, iterations=2)
e = ndi.binary_closing(e, structure=np.ones((3, 3)), iterations=ci)
m = ndi.binary_fill_holes(e)
lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n + 1)); m = lab == 1 + int(np.argmax(sz))
if len(sys.argv) > 9:   # optional manual circle (cap ball) cx cy r ymax, unioned into the mask
    cx, cy, r, ymax = map(float, sys.argv[6:10]) if len(sys.argv) > 9 else (0, 0, 0, 0)
    yy, xx = np.mgrid[0:m.shape[0], 0:m.shape[1]]
    m |= ((xx - cx) ** 2 + (yy - cy) ** 2 <= r * r) & (yy <= ymax)
m = ndi.binary_erosion(m, iterations=3); m = ndi.binary_opening(m, structure=np.ones((3, 3)), iterations=6)
m = ndi.binary_dilation(m, iterations=1)
a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.0); a = np.clip((a - .25) / .5, 0, 1)
ys, xs = np.where(a > .02); rgba = np.dstack([im, (a * 255).astype(np.uint8)])
Image.fromarray(rgba).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(dst); print(dst, xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)
