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

def rr(x0, y0, x1, y1, r=6):
    return [(x0 + r, y0), (x1 - r, y0), (x1, y0 + r), (x1, y1 - r), (x1 - r, y1), (x0 + r, y1), (x0, y1 - r), (x0, y0 + r)]

if __name__ == '__main__':
    A = 'assets/source/'; C = 'assets/cutouts/'
    # Treasure: cap + rectangular gold body
    cut(A + 'mad_treasure_original.webp', C + 'mad_treasure.png',
        [rr(179, 192, 301, 320, 2), rr(128, 312, 351, 727, 7)], overlay='/tmp/crops/o_treasure.png')
    # Naxos (grid scale .55, origin 200,0)
    n = [(283,330),(262,340),(240,352),(205,395),(180,430),(171,480),(170,560),(172,650),(190,720),(215,785),(240,825),(290,832),(420,832),(448,800),(478,740),(500,690),(511,640),(511,470),(490,400),(450,355),(410,332),(412,290),(410,230),(408,180),(372,115),(350,92),(333,75),(316,92),(290,130),(277,180),(275,230),(278,290)]
    cut(A + 'naxos_shoprescuespa.jpg', C + 'naxos.png', [tx(n, 200, 0, .55)], overlay='/tmp/crops/o_naxos.png', erode=0)
    # Marjorie (grid scale 1.7, origin 270,100)
    mj = [(215,205),(180,235),(150,285),(125,345),(105,420),(92,490),(100,560),(112,650),(125,730),(140,790),(158,808),(210,812),(300,812),(354,810),(369,791),(384,736),(399,680),(413,600),(421,520),(415,430),(400,340),(375,260),(335,215),(300,205)]
    cut(A + 'mad_marjorie_original.webp', C + 'mad_marjorie.png', [tx(mj, 270, 100, 1.7), tx([(226,208),(222,185),(240,168),(268,168),(286,185),(290,208)],270,100,1.7)],
        circles=[(270 + 255 / 1.7, 100 + 135 / 1.7, 85 / 1.7)], overlay='/tmp/crops/o_marj.png', erode=0)
