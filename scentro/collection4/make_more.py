"""Extra men's Selective bottles: (1) originals from the MAD Selective PDF (image + soft mask), (2) MAD bottle cutouts for the new codes,
reusing the consensus silhouette already applied to the first ten bottles (same glass, same camera)."""
import sys, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
PDFX = sys.argv[1]            # folder with pdfimages -png output of pages 19-27 (pg-NNN.png); PDFX18 = same for page 18 only
PDFX18 = sys.argv[2]
ORIG = {'orig_bhero': 24, 'orig_aventus': 28, 'orig_sauvage_edp': 51, 'orig_dior_homme_intense': 55, 'orig_invictus_parfum': 106,
        'orig_scandal_absolu': 160, 'orig_azzaro_wanted': 164, 'orig_armani_swy_edt': 222, 'orig_armani_adg': 249, 'orig_tf_black_orchid': -18}
for name, n in ORIG.items():
    PD = PDFX
    if n < 0: PD, n = PDFX18, -n
    im = Image.open(f'{PD}/pg-{n:03d}.png').convert('RGB'); a = Image.open(f'{PD}/pg-{n+1:03d}.png').convert('L')
    rgba = im.copy(); rgba.putalpha(a); bb = a.point(lambda v: 255 if v > 10 else 0).getbbox(); rgba.crop(bb).save(f'collection4/assets/cutouts/{name}.png'); print(name, bb)
A = np.array(Image.open('collection4/assets/cutouts/y102.png').getchannel('A'))
for code in 'a102 a105 a114 b103 j110 w158 w179 w183'.split():
    im = Image.open(f'collection4/assets/source/{code}_scentrojo_packshot.webp').convert('RGB'); W, H = im.size
    crop = np.array(im.crop((int(W * .57), 0, W, H))).astype(float)
    bg = np.median(np.concatenate([crop[:12].reshape(-1, 3), crop[-12:].reshape(-1, 3), crop[:, -12:].reshape(-1, 3)]), axis=0)
    m = np.abs(crop - bg).max(axis=2) > 9
    m = ndi.binary_closing(m, iterations=5); m = ndi.binary_fill_holes(m); lab, k = ndi.label(m); sz = ndi.sum(m, lab, range(1, k + 1)); m = lab == 1 + int(np.argmax(sz)); m = ndi.binary_opening(m, iterations=2)
    ys, xs = np.where(m); box = Image.fromarray(crop.astype(np.uint8)).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).resize((237, 570), Image.LANCZOS)
    Image.fromarray(np.dstack([np.array(box), A]), 'RGBA').save(f'collection4/assets/cutouts/{code}.png'); print(code, (xs.min(), ys.min(), xs.max(), ys.max()))
