"""Hybrid cutout: edge-based mask above `ysplit`, hand-traced polygon below (for pale glass bases that merge with the backdrop).
Usage: cutout_hybrid.py in out lo hi ysplit 'x,y x,y ...'"""
import sys, numpy as np, cv2
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
src, dst, lo, hi, ys = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
poly = [tuple(map(float, p.split(','))) for p in sys.argv[6].split()]
im = np.array(Image.open(src).convert('RGB')); g = cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_RGB2GRAY), (0, 0), 1.2)
e = ndi.binary_dilation(cv2.Canny(g, lo, hi) > 0, iterations=2); e = ndi.binary_closing(e, structure=np.ones((3, 3)), iterations=7)
m = ndi.binary_fill_holes(e); lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n + 1)); m = lab == 1 + int(np.argmax(sz))
m = ndi.binary_erosion(m, iterations=3); m = ndi.binary_opening(m, structure=np.ones((3, 3)), iterations=6); m = ndi.binary_dilation(m, iterations=1)
m[ys:] = False
S = 4; pm = Image.new('L', (im.shape[1] * S, im.shape[0] * S), 0); ImageDraw.Draw(pm).polygon([(x * S, y * S) for x, y in poly], fill=255)
pm = np.array(pm.resize((im.shape[1], im.shape[0]), Image.LANCZOS)) > 127
pm[:ys - 12] = False
m = m | pm
a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.9); a = np.clip((a - .25) / .5, 0, 1)
yy, xx = np.where(a > .02); rgba = np.dstack([im, (a * 255).astype(np.uint8)])
Image.fromarray(rgba).crop((xx.min(), yy.min(), xx.max() + 1, yy.max() + 1)).save(dst); print(dst, xx.max() - xx.min() + 1, yy.max() - yy.min() + 1)
