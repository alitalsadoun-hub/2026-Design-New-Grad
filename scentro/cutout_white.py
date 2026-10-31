"""Cutout for bottles on near-white backgrounds: low-threshold difference mask + hole fill. Usage: in out thr"""
import sys, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
im = np.array(Image.open(sys.argv[1]).convert('RGB')); thr = float(sys.argv[3])
diff = (255 - im.astype(float)).max(axis=2)
m = diff > thr
m = ndi.binary_closing(m, iterations=6); m = ndi.binary_fill_holes(m)
lab, n = ndi.label(m); sizes = ndi.sum(m, lab, range(1, n + 1)); m = lab == 1 + int(np.argmax(sizes))
m = ndi.binary_opening(m, iterations=2)
a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.0); a = np.clip((a - .2) / .6, 0, 1)
ys, xs = np.where(a > .02); rgba = np.dstack([im, (a * 255).astype(np.uint8)])
Image.fromarray(rgba).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(sys.argv[2]); print('ok')
