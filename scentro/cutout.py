"""Background removal via GrabCut -> RGBA PNG. Usage: cutout.py in out x0 y0 x1 y1"""
import sys, cv2, numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, dst = sys.argv[1], sys.argv[2]
x0,y0,x1,y1 = map(int, sys.argv[3:7])
im = np.array(Image.open(src).convert('RGB'))
bgr = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
mask = np.full(im.shape[:2], cv2.GC_BGD, np.uint8)
mask[y0:y1, x0:x1] = cv2.GC_PR_BGD
# seed: pixels clearly different from the border background colour = probable foreground
border = np.concatenate([im[0], im[-1], im[:,0], im[:,-1]]).reshape(-1,3).mean(0)
diff = np.linalg.norm(im.astype(float)-border, axis=2)
roi = np.zeros_like(mask, bool); roi[y0:y1, x0:x1] = True
mask[roi & (diff > 45)] = cv2.GC_PR_FGD
mask[roi & (diff > 110)] = cv2.GC_FGD
b = np.zeros((1,65)); f = np.zeros((1,65))
cv2.grabCut(bgr, mask, None, b, f, 8, cv2.GC_INIT_WITH_MASK)
m = np.isin(mask, (cv2.GC_FGD, cv2.GC_PR_FGD))
lab, n = ndi.label(m)
if n:
    sizes = ndi.sum(m, lab, range(1, n+1)); m = lab == (1+int(np.argmax(sizes)))
m = ndi.binary_fill_holes(m)
m = ndi.binary_opening(m, iterations=1)
a = cv2.GaussianBlur(m.astype(np.float32), (0,0), 0.9)
a = np.clip((a-0.15)/0.7, 0, 1)
ys, xs = np.where(a > 0.02)
rgba = np.dstack([im, (a*255).astype(np.uint8)])
Image.fromarray(rgba).crop((xs.min(), ys.min(), xs.max()+1, ys.max()+1)).save(dst)
print(dst, xs.max()-xs.min()+1, ys.max()-ys.min()+1)
