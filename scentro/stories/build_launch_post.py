"""SCENTRO feed post 4:5 (1080x1350): "our new website is live" - same artwork as the Story, recomposed for the post format.
Real photos only (MAD Rouge + Bruno Detox cutouts, real screenshot of the live site in a drawn phone frame).
Usage (from scentro/):  python3 stories/build_launch_post.py   ->  stories/output/scentro_new_website_launch_post_4x5.png"""
import os, sys, subprocess
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_launch as L        # phone(), also chdir()s to scentro/
import build_stories as S
import build_slide as B

W, H = 1080, 1350
A = 'stories/assets/cutouts/'
HTML = """<!doctype html><html lang="ar"><head><meta charset="utf-8"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cormorant+Garamond:wght@500;600;700&family=IBM+Plex+Sans+Arabic:wght@400;500;600&family=Inter:wght@500;600&display=swap" rel="stylesheet">
<style>
html,body{margin:0;background:transparent;width:1080px;height:1350px;overflow:hidden}
.t{position:absolute;left:0;width:1080px;text-align:center;white-space:nowrap}
.logo{top:52px;font:500 42px 'Cormorant Garamond',serif;letter-spacing:20px;color:#4A3428;padding-left:20px}
.rule{position:absolute;left:517px;top:126px;width:46px;height:2px;background:#B08D57}
.h{top:150px;font:700 104px/1.25 'Amiri',serif;color:#701C2C}
.rule2{position:absolute;left:500px;top:322px;width:80px;height:2px;background:#B08D57}.dot{position:absolute;left:536px;top:318px;width:8px;height:8px;border-radius:50%;background:#B08D57}
.sub{top:344px;font:600 23px 'Inter',sans-serif;letter-spacing:12px;color:#8F6934;padding-left:12px}
.ofa{top:1236px;font:500 36px 'IBM Plex Sans Arabic',sans-serif;color:#4A3428}
.ofe{top:1296px;font:600 17px 'Inter',sans-serif;letter-spacing:6px;color:#8F6934;padding-left:6px}
</style></head><body>
<div class="t logo">SCENTRO</div><div class="rule"></div>
<div class="t h">موقعنا بحلّته الجديدة</div>
<div class="rule2"></div><div class="dot"></div>
<div class="t sub">OUR NEW WEBSITE IS LIVE</div>
<div class="t ofa">أي عطر نيش بـ ٣٠ دينار · حتى نهاية شهر ١١</div>
<div class="t ofe">ANY NICHE PERFUME 30 JOD · UNTIL 30 NOV</div>
</body></html>"""


def build():
    s = dict(bg_a=(246, 238, 226), bg_b=(232, 217, 198), niche_rgb=(227, 208, 186), stone=(2, 0, -3))
    img = B.background(s)
    S.glow(img, 330, 760, 420, 460, (214, 150, 150), 0.10); S.glow(img, 780, 740, 420, 440, (255, 228, 192), 0.20)
    B.niche(img, s); B.travertine(img, s)
    rg = B.load_clean(A + 'rouge_hi.png', 400); bd = B.load_clean(A + 'bd_bottle.png', 362); ph = L.phone(screen_w=250, bezel=10, radius=44)
    B.stage_bottle(img, rg, 300, B.BASE_Y); B.stage_bottle(img, bd, 784, B.BASE_Y)
    B.stage_bottle(img, ph, 540, B.BASE_Y)
    open('/tmp/claude-0/launch_post.html', 'w', encoding='utf-8').write(HTML)
    tl = '/tmp/claude-0/launch_post_text.png'
    subprocess.run(['node', 'stories/render_text.js', '/tmp/claude-0/launch_post.html', tl, str(W), str(H)], check=True)
    out = Image.alpha_composite(img.convert('RGBA'), Image.open(tl).convert('RGBA')).convert('RGB')
    assert out.size == (W, H)
    p = 'stories/output/scentro_new_website_launch_post_4x5.png'; out.save(p, optimize=True); print(p, out.size)


if __name__ == '__main__':
    build()
