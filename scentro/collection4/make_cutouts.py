"""MAD Selective 100 ml bottle cutouts for the men's carousel: from the 'box + bottle' packshot in each Scentro product gallery.
Crops the bottle half, builds a difference mask against the near-white backdrop (like cutout_white.py), fills the glass, softens the edge."""
import sys, glob, os, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
THR = float(sys.argv[1]) if len(sys.argv) > 1 else 9
for fn in sorted(glob.glob('collection4/assets/source/*_scentrojo_packshot.webp')):
    code = os.path.basename(fn).split('_')[0]
    im = Image.open(fn).convert('RGB'); W, H = im.size
    x0 = int(W * 0.57); crop = np.array(im.crop((x0, 0, W, H))).astype(float)
    # backdrop = local median of the border pixels (the wall/floor gradient is very soft)
    bg = np.median(np.concatenate([crop[:12].reshape(-1, 3), crop[-12:].reshape(-1, 3), crop[:, -12:].reshape(-1, 3)]), axis=0)
    diff = np.abs(crop - bg).max(axis=2)
    m = diff > THR
    m = ndi.binary_closing(m, iterations=5); m = ndi.binary_fill_holes(m)
    lab, n = ndi.label(m); sizes = ndi.sum(m, lab, range(1, n + 1)); m = lab == 1 + int(np.argmax(sizes))
    m = ndi.binary_opening(m, iterations=2)
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.0); a = np.clip((a - .2) / .6, 0, 1)
    ys, xs = np.where(a > .02); rgba = np.dstack([crop.astype(np.uint8), (a * 255).astype(np.uint8)])
    out = Image.fromarray(rgba).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)); out.save(f'collection4/assets/cutouts/{code}.png'); print(code, out.size)

# ---- consensus pass: every MAD Selective bottle is the same glass shape, shot with the same camera, so build ONE clean silhouette
# from the 10 masks (pixel is bottle if >=3 of 10 agree) and apply it to each photo. Fixes missing chunks of clear glass.
files = sorted(f for f in glob.glob('collection4/assets/cutouts/*.png') if not os.path.basename(f).startswith('orig_'))
ims = [Image.open(f).convert('RGBA') for f in files]; Wc, Hc = 237, 570
al = np.stack([np.array(i.getchannel('A').resize((Wc, Hc), Image.BILINEAR)).astype(np.float32) / 255 for i in ims])
cons = al.mean(0) > 0.3
cons = ndi.binary_closing(cons, iterations=6); cons = ndi.binary_fill_holes(cons); cons = ndi.binary_opening(cons, iterations=2)
lab, n = ndi.label(cons); sizes = ndi.sum(cons, lab, range(1, n + 1)); cons = lab == 1 + int(np.argmax(sizes))
A = cv2.GaussianBlur(cons.astype(np.float32), (0, 0), 1.1); A = np.clip((A - .15) / .7, 0, 1)
for f, i in zip(files, ims):
    rgb = np.array(i.convert('RGB').resize((Wc, Hc), Image.LANCZOS)); out = Image.fromarray(np.dstack([rgb, (A * 255).astype(np.uint8)]), 'RGBA'); out.save(f)
print('consensus silhouette applied to', len(files), 'bottles; coverage', round(float(cons.mean()), 3))
