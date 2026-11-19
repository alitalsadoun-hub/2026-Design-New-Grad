"""Builds Scentro-style product images for Tom Ford Q105 / Q110: MAD unisex Selective 100 ml bottle+box (from the Q106 gallery)
with the original perfume (cut from the MAD Selective catalogue page) in front, like the existing Selective photos.
usage: python3 make_tomford_images.py <catalogue_page_png_dir> <q106_gallery_image> <out_dir>"""
import sys, numpy as np, cv2
from PIL import Image, ImageFilter
pages, base_fp, out = sys.argv[1:4]
def cut(page, box):
    im = Image.open(f'{pages}/pg-{page:02d}.png').convert('RGB'); f = im.size[0] / 582
    c = np.array(im.crop(tuple(int(v * f) for v in box)))
    h, w = c.shape[:2]; mask = np.zeros((h + 2, w + 2), np.uint8); work = c.copy()
    for seed in [(1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2), (w // 2, 1), (w // 2, h - 2), (1, h // 2), (w - 2, h // 2)]:
        cv2.floodFill(work, mask, seed, (0, 0, 0), (22, 22, 22), (22, 22, 22), cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE | (255 << 8))
    bg = mask[1:-1, 1:-1] > 0
    alpha = (~bg).astype(np.uint8) * 255
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(alpha); keep = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA]); alpha = (lab == keep).astype(np.uint8) * 255
    alpha = cv2.GaussianBlur(alpha, (0, 0), 1.2)
    ys, xs = np.where(alpha > 20); rgba = np.dstack([c, alpha])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return Image.fromarray(rgba, 'RGBA')
def compose(orig, name):
    base = Image.open(base_fp).convert('RGB'); W, H = base.size
    h = int(H * 0.40); o = orig.resize((int(orig.width * h / orig.height), h), Image.LANCZOS)
    x, y = int(W * 0.06), int(H * 0.50)
    sh = Image.new('L', base.size, 0); a = o.getchannel('A')
    sh.paste(a.point(lambda v: int(v * .55)).transform(a.size, Image.AFFINE, (1, 0, -14, 0, 1, 4)), (x, y + 6))
    sh = sh.filter(ImageFilter.GaussianBlur(14)); base.paste(Image.new('RGB', base.size, (70, 55, 42)), (0, 0), sh)
    base.paste(o, (x, y), o); base.save(f'{out}/{name}.jpg', quality=90)
cut_q110 = cut(17, (75, 468, 198, 640)); cut_q105 = cut(18, (375, 75, 500, 248))
compose(cut_q110, 'tf_q110'); compose(cut_q105, 'tf_q105'); print('ok')
