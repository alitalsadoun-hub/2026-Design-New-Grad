"""CTA end-screen layers, drawn natively at 2160x3840 (crisp text, not upscaled). Safe area: all content between y~1200 and y~3000 of 3840."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
WO, HO = 2160, 3840
CORM = '../fonts/CormorantGaramond-VF.ttf'; INTER_M = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'
BROWN, GOLD, GOLD_D = (74, 52, 40), (176, 141, 87), (143, 105, 52)

def font(p, s, var=None):
    f = ImageFont.truetype(p, s)
    if var: f.set_variation_by_name(var)
    return f

def background():
    yy, xx = np.mgrid[0:HO, 0:WO].astype(np.float32)
    t = np.clip(xx / WO * 0.30 + yy / HO * 0.85, 0, 1)[..., None]
    img = np.array([248, 241, 230], np.float32) * (1 - t) + np.array([236, 222, 203], np.float32) * t
    img += 10 * np.clip(1 - np.hypot((xx - 700) / 1900, (yy - 700) / 1700), 0, 1)[..., None] ** 2           # soft window-light bloom
    img *= 1 - 0.06 * np.clip(np.hypot((xx - WO / 2) / (WO * .8), (yy - HO * .5) / (HO * .75)) - .35, 0, 1)[..., None]
    img += np.random.default_rng(3).normal(0, 0.9, (HO, WO, 1))
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA')
    # thin gold arch outline echoing the brand arch (kept faint)
    cx, top, R, bot = WO // 2, 860, 900, 2700
    d.arc((cx - R, top, cx + R, top + 2 * R), 180, 360, fill=GOLD + (120,), width=4)
    d.line((cx - R, top + R, cx - R, bot), fill=GOLD + (120,), width=4); d.line((cx + R, top + R, cx + R, bot), fill=GOLD + (120,), width=4)
    return im.convert('BGR' if False else 'RGB')

def tracked(txt, f, fill, track, pad=40):
    ws = [f.getlength(c) for c in txt]; w = int(sum(ws) + track * (len(txt) - 1)) + 2 * pad; h = int(f.size * 1.7)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = pad
    for c, cw in zip(txt, ws): d.text((x, h // 2), c, font=f, fill=fill, anchor='lm'); x += cw + track
    return im

def line(w, th=5):
    im = Image.new('RGBA', (w, th + 4), (0, 0, 0, 0)); ImageDraw.Draw(im).rectangle((0, 2, w, 2 + th - 1), fill=GOLD + (255,)); return im

def layers():
    """-> list of (RGBA image, centre_x, centre_y, start_delay_s)"""
    L = []
    L.append((tracked('SCENTRO', font(CORM, 170, 'Medium'), BROWN, 46), WO // 2, 1380, 0.0))
    L.append((line(190), WO // 2, 1565, 0.15))
    L.append((tracked('Discover Your Signature Scent', font(CORM, 104, 'Medium'), BROWN, 4), WO // 2, 1745, 0.3))
    L.append((tracked('SHOP ONLINE', font(INTER_M, 54), GOLD_D, 24), WO // 2, 2120, 0.5))
    url = tracked('scentrojo.com', font(CORM, 250, 'SemiBold'), BROWN, 6)
    L.append((url, WO // 2, 2340, 0.7))
    L.append((line(url.width - 110, 7), WO // 2, 2505, 0.9))
    return L

if __name__ == '__main__':
    bg = background().convert('RGBA')
    for im, cx, cy, _ in layers(): bg.alpha_composite(im, (cx - im.width // 2, cy - im.height // 2))
    bg.convert('RGB').resize((1080, 1920), Image.LANCZOS).save('/tmp/claude-0/-home-user-2026-Design-New-Grad/69a2305f-cc46-55cb-9e90-d1dd6b9b345c/scratchpad/cta_preview.png')
    print([ (im.width, im.height) for im,_,_,_ in layers()])
