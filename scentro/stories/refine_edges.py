"""Smooth a jagged / light-fringed cutout alpha: blur -> re-threshold (removes sawtooth), erode `er` px, feather. Pixels are never repainted.
Usage: refine_edges.py in.png out.png sigma erode"""
import sys, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
src, dst, sg, er = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
a = np.array(Image.open(src).convert('RGBA')); al = a[..., 3].astype(np.float32) / 255
m = cv2.GaussianBlur(al, (0, 0), sg) > 0.5
m = ndi.binary_fill_holes(m)
if er: m = ndi.binary_erosion(m, iterations=er)
f = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8); f = np.clip((f - .15) / .7, 0, 1)
a[..., 3] = (f * 255).astype(np.uint8)
ys, xs = np.where(a[..., 3] > 4); Image.fromarray(a).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(dst); print(dst, xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)
