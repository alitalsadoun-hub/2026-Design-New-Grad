"""SCENTRO women's collection Reel: 10 plates (1080x1920) -> 2160x3840 @30fps, slow push-in + soft crossfades, no audio.
Frames are resampled with sub-pixel cubic interpolation (no zoompan jitter) and piped to ffmpeg (libx264)."""
import subprocess, sys, numpy as np, cv2
from PIL import Image
import cta_layers
CODES = ['a113', 'a118', 'b103', 'b105', 'b107', 'd116', 'g102', 'k102', 'w213', 'y104']
FPS, D, O = 30, 3.5, 0.7                 # clip length, crossfade overlap (s)  -> total 10*3.5 - 9*0.7 = 28.7 s
WO, HO = 2160, 3840
Z0, Z1, DY = 1.020, 1.105, -30.0         # slow push-in; tiny upward drift (source px)
IVORY = np.array([228, 238, 245], np.float32)   # BGR ivory used for the fade in / out
plates = [cv2.imread(f'plate_{c}.png') for c in CODES]
step = D - O; main_end = len(CODES) * D - (len(CODES) - 1) * O          # 28.7 s of perfumes
XF, CTA_LEN = 0.9, 4.0                                                  # crossfade into CTA; CTA clip length (3.1 s solo)
cs = main_end - XF; total = cs + CTA_LEN; NF = round(total * FPS)       # total 31.8 s
CTA_BG = cv2.cvtColor(np.asarray(cta_layers.background()), cv2.COLOR_RGB2BGR).astype(np.float32)
CTA_L = []
for im, cx, cy, dl in cta_layers.layers():
    a = np.asarray(im).astype(np.float32); rgb = a[..., :3][..., ::-1]; al = a[..., 3:] / 255.0
    CTA_L.append((rgb, al, cx - im.width // 2, cy - im.height // 2, dl))

def cta_frame(t):
    f = CTA_BG.copy(); tt = t - cs - 0.7                               # text starts once the background is mostly in
    for rgb, al, x, y, dl in CTA_L:
        k = float(ease((tt - dl) / 0.6))
        if k <= 0: continue
        y2 = y + int(round((1 - k) * 26)); h, w = al.shape[:2]
        reg = f[y2:y2 + h, x:x + w]; a = al * k
        f[y2:y2 + h, x:x + w] = reg * (1 - a) + rgb * a
    return f
ease = lambda x: 0.5 - 0.5 * np.cos(np.pi * np.clip(x, 0, 1))
rng = np.random.default_rng(1)

def view(i, t):
    """One continuous, very slow push-in shared by every clip, so slides sit at the same scale during each dissolve (no ghosted double text)."""
    g = np.clip(t / main_end, 0, 1)
    z = Z0 + (Z1 - Z0) * g; s = 2.0 * z
    cx, cy = 540.0, 960.0 + DY * g
    M = np.array([[s, 0, -s * cx + WO / 2], [0, s, -s * cy + HO / 2]], np.float32)
    return cv2.warpAffine(plates[i], M, (WO, HO), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)

cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{WO}x{HO}', '-r', str(FPS), '-i', '-',
       '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '13', '-profile:v', 'high', '-level', '5.1', '-pix_fmt', 'yuv420p',
       '-vf', 'scale=in_range=full:out_range=tv:out_color_matrix=bt709', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
       '-color_range', 'tv', '-movflags', '+faststart', '-r', str(FPS), 'scentro_women_reel_4k.mp4']
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for n in range(NF):
    t = n / FPS
    act = [i for i in range(len(CODES)) if i * step <= t < i * step + D]
    if t >= cs + XF: f = cta_frame(t)
    elif t >= cs:                                                       # last perfume -> CTA crossfade
        k = ease((t - cs) / XF); f = (1 - k) * view(act[-1], t) + k * cta_frame(t)
    elif len(act) == 1: f = view(act[0], t)
    else:
        a, b = act[0], act[1]; k = ease((t - b * step) / O)           # crossfade a -> b
        f = (1 - k) * view(a, t) + k * view(b, t)
    if t < 0.6: f = IVORY + (f - IVORY) * ease(t / 0.6)                # fade in from ivory
    f += rng.normal(0, 0.7, f.shape[:2])[..., None]                    # imperceptible dither against banding
    p.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
    if n % 60 == 0: print(f'frame {n}/{NF}', flush=True)
p.stdin.close(); p.wait(); print('done', NF, 'frames', total, 's')
