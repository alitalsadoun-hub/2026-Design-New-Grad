"""Hand-traced polygon cutouts for low-contrast bottles (bottle shape traced on the real photo; pixels are never redrawn)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
def tx(pts, ox, oy, s): return [(ox + x / s, oy + y / s) for x, y in pts]
def cut(src, dst, polys, circles=(), erode=1.0, overlay=None):
    im = Image.open(src).convert('RGB'); S = 4
    m = Image.new('L', (im.width * S, im.height * S), 0); d = ImageDraw.Draw(m)
    for p in polys: d.polygon([(x * S, y * S) for x, y in p], fill=255)
    for cx, cy, r in circles: d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=255)
    m = m.resize(im.size, Image.LANCZOS)
    if erode: m = m.filter(ImageFilter.MinFilter(3)) if erode >= 1 else m
    m = m.filter(ImageFilter.GaussianBlur(0.6))
    if overlay:
        o = im.copy(); ImageDraw.Draw(o).line([p for poly in polys for p in poly + [poly[0]]], fill=(0, 255, 0), width=1); o.save(overlay)
    rgba = im.convert('RGBA'); rgba.putalpha(m)
    bb = m.point(lambda v: 255 if v > 5 else 0).getbbox(); rgba.crop(bb).save(dst); print(dst, bb)

def chaikin(p, n=3):
    for _ in range(n):
        q = []
        for i in range(len(p)):
            a, b = p[i], p[(i + 1) % len(p)]
            q += [(.75 * a[0] + .25 * b[0], .75 * a[1] + .25 * b[1]), (.25 * a[0] + .75 * b[0], .25 * a[1] + .75 * b[1])]
        p = q
    return p

def rr(x0, y0, x1, y1, r=6):
    return [(x0 + r, y0), (x1 - r, y0), (x1, y0 + r), (x1, y1 - r), (x1 - r, y1), (x0 + r, y1), (x0, y1 - r), (x0, y0 + r)]

if __name__ == '__main__':
    A = 'assets/source/'; C = 'assets/cutouts/'
    # Treasure: cap + rectangular gold body
    cut(A + 'mad_treasure_original.webp', C + 'mad_treasure.png',
        [rr(179, 192, 301, 320, 2), rr(128, 312, 351, 727, 7)], overlay='/tmp/crops/o_treasure.png')
    # Naxos (grid scale .55, origin 200,0)
    n = [(283,330),(262,340),(240,352),(205,395),(180,430),(171,480),(170,560),(172,650),(190,720),(215,785),(240,825),(290,832),(420,832),(448,800),(478,740),(500,690),(511,640),(511,470),(490,400),(450,355),(410,332),(412,290),(410,230),(408,180),(372,115),(350,92),(333,75),(316,92),(290,130),(277,180),(275,230),(278,290)]
    cut(A + 'naxos_shoprescuespa.jpg', C + 'naxos.png', [chaikin(tx(n, 200, 0, .55))], overlay='/tmp/crops/o_naxos.png', erode=0)
    # Marjorie: silhouette traced on a 3x zoom grid (absolute source coords), incl. both dark glass side walls
    L=[(397,217),(376,222),(360,243),(343,270),(331,303),(322,340),(319,400),(321,440),(327,480),(340,520),(352,550),(360,572)]
    R=[(476,572),(480,550),(487,520),(497,480),(506,440),(512,400),(514,340),(510,300),(497,270),(480,245),(460,224),(440,217)]
    body=chaikin(L+[(372,578),(418,580),(464,578)]+R,2)
    neck=[(395,198),(443,198),(446,219),(392,219)]
    cut(A + 'mad_marjorie_original.webp', C + 'mad_marjorie.png', [body, neck], circles=[(419,191,50)],
        overlay='/tmp/crops/o_marj.png', erode=0)
