"""Favicon set + social share image (og.jpg) for SCENTRO. Run from concept_v3: python3 tools_make_brand_assets.py"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
GOLD=(211,182,109); BLACK=(12,11,10)
F='../../scentro/fonts/CormorantGaramond-VF.ttf'
def font(sz,w='SemiBold'):
    f=ImageFont.truetype(F,sz)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
# favicon: gold S on black rounded square
def icon(size):
    S=size*4; im=Image.new('RGB',(S,S),BLACK); d=ImageDraw.Draw(im); d.rounded_rectangle((0,0,S,S),radius=int(S*.22),fill=BLACK)
    f=font(int(S*.8)); bb=d.textbbox((0,0),'S',font=f); w,h=bb[2]-bb[0],bb[3]-bb[1]
    d.text(((S-w)/2-bb[0],(S-h)/2-bb[1]-S*.02),'S',font=f,fill=GOLD)
    return im.resize((size,size),Image.LANCZOS)
for n,s in [('apple-touch-icon.png',180),('icon-192.png',192),('icon-512.png',512),('favicon-32.png',32)]: icon(s).save('img/'+n,optimize=True)
icon(64).save('img/favicon.ico',sizes=[(16,16),(32,32),(48,48),(64,64)])
# og image 1200x630
W,H=1200,630; bg=Image.open('img/hero_scene.jpg').convert('RGB'); r=max(W/bg.width,H/bg.height); bg=bg.resize((int(bg.width*r),int(bg.height*r)),Image.LANCZOS)
bg=bg.crop(((bg.width-W)//2,(bg.height-H)//2,(bg.width-W)//2+W,(bg.height-H)//2+H)).filter(ImageFilter.GaussianBlur(1))
ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
for x in range(W): d.line((x,0,x,H),fill=(12,11,10,int(250*min(1,max(0,(0.80*W-x)/(0.38*W))))))
bg=Image.alpha_composite(bg.convert('RGBA'),ov).convert('RGB')
logo=Image.open('img/logo_light.png').convert('RGBA'); lw=420; logo=logo.resize((lw,int(logo.height*lw/logo.width)),Image.LANCZOS); bg.paste(logo,(70,150),logo)
d=ImageDraw.Draw(bg)
d.text((72,150+logo.height+40),'Niche & Selective Perfumes',font=font(40,'Medium'),fill=(239,229,211))
d.text((72,150+logo.height+100),'Delivery across Jordan',font=ImageFont.truetype(F,30),fill=GOLD)
bg.save('img/og.jpg',quality=88,optimize=True); print('ok')
