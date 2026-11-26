"""SCENTRO Story: "our new website is live" (1080x1920).
Real photos only: MAD Rouge + MAD Bruno Detox cutouts (from the niche offer Story) and a real screenshot of the live site (scentrojo.com, mobile, Arabic) in a drawn phone frame.
Text is rendered in Chromium (Arabic shaping + Amiri / Cormorant web fonts) on a transparent layer and composited over the Pillow scene.
Usage (from scentro/):  python3 stories/build_launch.py    ->  stories/output/scentro_new_website_launch_story.png
Safe zones: nothing important above y=250 or below y=1620; the link-sticker zone (y 1560-1640) is left clear."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_stories as S          # also chdir()s to scentro/
import build_slide as B

W, H = S.W, S.H
A = 'stories/assets/cutouts/'
SHOT = 'stories/assets/launch/site_home_ar.png'


def phone(screen_w=336, bezel=13, radius=54):
    kk = screen_w / 336                                                          # everything scales with the screen width
    shot = Image.open(SHOT).convert('RGB')
    pad = Image.new('RGB', (shot.width, shot.height + 165), (14, 12, 10)); pad.paste(shot, (0, 165)); shot = pad   # status-bar band above the site so the phone's camera island never covers the site's top bar
    sh = int(screen_w * shot.height / shot.width); shot = shot.resize((screen_w, sh), Image.LANCZOS)
    pw, ph = screen_w + 2 * bezel, sh + 2 * bezel; k = 3                          # draw at 3x for smooth edges
    body = Image.new('RGBA', (pw * k, ph * k), (0, 0, 0, 0)); d = ImageDraw.Draw(body)
    d.rounded_rectangle((0, 0, pw * k - 1, ph * k - 1), radius=radius * k, fill=(176, 141, 87, 255))                      # thin gold rim
    d.rounded_rectangle((2 * k, 2 * k, pw * k - 3 * k, ph * k - 3 * k), radius=(radius - 2) * k, fill=(16, 14, 12, 255))  # black glass body
    mask = Image.new('L', (pw * k, ph * k), 0); ImageDraw.Draw(mask).rounded_rectangle((bezel * k, bezel * k, (bezel + screen_w) * k, (bezel + sh) * k), radius=(radius - bezel) * k, fill=255)
    scr = Image.new('RGBA', (pw * k, ph * k), (0, 0, 0, 0)); scr.paste(shot.resize((screen_w * k, sh * k), Image.LANCZOS), (bezel * k, bezel * k)); body.paste(scr, (0, 0), mask)
    d = ImageDraw.Draw(body); iw, ih, iy = int(46 * kk), int(26 * kk), int(12 * kk); d.rounded_rectangle(((pw // 2 - iw) * k, (bezel + iy) * k, (pw // 2 + iw) * k, (bezel + iy + ih) * k), radius=ih // 2 * k, fill=(16, 14, 12, 255))  # dynamic island
    return body.resize((pw, ph), Image.LANCZOS)


HTML = """<!doctype html><html lang="ar"><head><meta charset="utf-8"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cormorant+Garamond:wght@500;600;700&family=IBM+Plex+Sans+Arabic:wght@400;500;600&family=Inter:wght@500;600&display=swap" rel="stylesheet">
<style>
html,body{margin:0;background:transparent;width:1080px;height:1920px;overflow:hidden}
.t{position:absolute;left:0;width:1080px;text-align:center;white-space:nowrap}
.logo{top:236px;font:500 46px 'Cormorant Garamond',serif;letter-spacing:22px;color:#4A3428;padding-left:22px}
.rule{position:absolute;left:517px;top:326px;width:46px;height:2px;background:#B08D57}
.h{top:366px;font:700 114px/1.25 'Amiri',serif;color:#701C2C}
.rule2{position:absolute;left:500px;top:528px;width:80px;height:2px;background:#B08D57}.dot{position:absolute;left:536px;top:524px;width:8px;height:8px;border-radius:50%;background:#B08D57}
.sub{top:548px;font:600 24px 'Inter',sans-serif;letter-spacing:12px;color:#8F6934;padding-left:12px}
.url{top:1452px;font:600 64px 'Cormorant Garamond',serif;letter-spacing:3px;color:#4A3428}
.ofa{top:1478px;font:500 38px 'IBM Plex Sans Arabic',sans-serif;color:#4A3428}
.ofe{top:1540px;font:600 18px 'Inter',sans-serif;letter-spacing:6px;color:#8F6934;padding-left:6px}
</style></head><body>
<div class="t logo">SCENTRO</div><div class="rule"></div>
<div class="t h">موقعنا بحلّته الجديدة</div>
<div class="rule2"></div><div class="dot"></div>
<div class="t sub">OUR NEW WEBSITE IS LIVE</div>
<div class="t ofa">أي عطر نيش بـ ٣٠ دينار · حتى نهاية شهر ١١</div>
<div class="t ofe">ANY NICHE PERFUME 30 JOD · UNTIL 30 NOV</div>
</body></html>"""


def text_layer(path):
    import subprocess
    open('/tmp/claude-0/launch.html', 'w', encoding='utf-8').write(HTML)
    subprocess.run(['node', 'stories/render_text.js', '/tmp/claude-0/launch.html', path, str(W), str(H)], check=True)


def build():
    S.canvas(arch_top=600, arch_r=470, surf_top=1370, surf_front=1655, base_y=1448)
    s = dict(bg_a=(246, 238, 226), bg_b=(232, 217, 198), niche_rgb=(227, 208, 186), stone=(2, 0, -3))
    img = B.background(s)
    S.glow(img, 360, 1000, 560, 640, (214, 150, 150), 0.10); S.glow(img, 760, 960, 560, 600, (255, 228, 192), 0.20)
    B.niche(img, s); B.travertine(img, s)
    rg = B.load_clean(A + 'rouge_hi.png', 540); bd = B.load_clean(A + 'bd_bottle.png', 480); ph = phone()
    B.stage_bottle(img, rg, 232, B.BASE_Y); B.stage_bottle(img, bd, 866, B.BASE_Y)
    B.stage_bottle(img, ph, 540, B.BASE_Y)
    tl = '/tmp/claude-0/launch_text.png'; text_layer(tl)
    out = Image.alpha_composite(img.convert('RGBA'), Image.open(tl).convert('RGBA')).convert('RGB')
    assert out.size == (W, H)
    os.makedirs('stories/output', exist_ok=True); p = 'stories/output/scentro_new_website_launch_story.png'; out.save(p, optimize=True); print(p, out.size)


if __name__ == '__main__':
    build()
