"""SCENTRO women's Reel v4 (final) - editorial cut edit, re-timed for the longer narration (MAD Parfumeur / Scentro retailer script) (no crossfades between perfumes).
Hard cuts placed on the narration's phrase boundaries; ONE continuous restrained camera path under the cuts (each shot ends on exactly the framing
the next shot starts with, so header/arch never jump at a cut); a single dissolve: last perfume -> plain CTA background; CTA text fades in after.
True 1080x1920 @30fps (frames supersampled at 2160x3840 then area-downscaled), H.264, silent video master."""
import subprocess, numpy as np, cv2
import cta_layers
ORDER = ['k102', 'w213', 'a118', 'y104', 'a113', 'b103', 'g102', 'b105', 'b107', 'd116']
CUTS = [1.40, 2.84, 4.15, 5.43, 7.30, 9.37, 11.25, 13.69, 16.03]              # cut times (s): voice gaps / phrase beats (voice 0.42-18.3 s)
MONTAGE_END, XF, CTA_SOLO = 18.30, 0.50, 2.80                                  # last shot ends / dissolve into CTA / CTA hold
FPS = 30; total = MONTAGE_END + XF + CTA_SOLO; NF = round(total * FPS)         # 21.6 s
WS, HS, WO, HO = 2160, 3840, 1080, 1920
BOUNDS = [0.0] + CUTS + [MONTAGE_END]
# camera states (zoom, dx, dy) at each cut; shot i moves S[i] -> S[i+1]. Tiny, varied: push / pull / drift / tilt (all within plate margins)
S = [(1.030, 0, 0), (1.055, -10, 14), (1.035, 8, -10), (1.060, -12, 12), (1.030, 0, -6), (1.050, 12, 10),
     (1.025, 0, -12), (1.055, -8, 8), (1.035, 10, -4), (1.060, 0, 6), (1.040, 0, 0)]
ease = lambda x: 0.5 - 0.5 * np.cos(np.pi * np.clip(x, 0, 1))
plates = {c: cv2.imread(f'plate_{c}.png') for c in ORDER}

def cam(i, t):
    u = ease((t - BOUNDS[i]) / (BOUNDS[i + 1] - BOUNDS[i]))
    a, b = np.array(S[i], float), np.array(S[i + 1], float); return a + (b - a) * u

def view(i, t):
    z, dx, dy = cam(i, min(t, BOUNDS[i + 1]))
    mx, my = 540 * (1 - 1 / z) * 0.95, 960 * (1 - 1 / z) * 0.95
    dx, dy = float(np.clip(dx, -mx, mx)), float(np.clip(dy, -my, my))
    s = 2.0 * z; cx, cy = 540 + dx, 960 + dy
    M = np.array([[s, 0, -s * cx + WS / 2], [0, s, -s * cy + HS / 2]], np.float32)
    return cv2.warpAffine(plates[ORDER[i]], M, (WS, HS), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)

CTA_BG = cv2.cvtColor(np.asarray(cta_layers.background(arch=False)), cv2.COLOR_RGB2BGR).astype(np.float32)   # plain: dissolve target has nothing to overlap
ARCH_A, ARCH_C = cta_layers.arch_alpha()
CTA_L = []
for im, cx, cy, dl in cta_layers.layers():
    a = np.asarray(im).astype(np.float32); CTA_L.append((a[..., :3][..., ::-1], a[..., 3:] / 255.0, cx - im.width // 2, cy - im.height // 2, dl))
def cta_frame(t, text_on=True):
    f = CTA_BG.copy(); tt = t - (MONTAGE_END + XF)
    if not text_on: return f
    ka = float(ease(tt / 0.6)); f = f * (1 - ARCH_A * ka) + ARCH_C * ARCH_A * ka          # arch outline fades in with the text, after the dissolve
    for rgb, al, x, y, dl in CTA_L:
        k = float(ease((tt - dl * 0.8) / 0.5))
        if k <= 0: continue
        y2 = y + int(round((1 - k) * 22)); h, w = al.shape[:2]; a = al * k
        f[y2:y2 + h, x:x + w] = f[y2:y2 + h, x:x + w] * (1 - a) + rgb * a
    return f

cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{WO}x{HO}', '-r', str(FPS), '-i', '-',
       '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '12', '-profile:v', 'high', '-level', '4.2', '-pix_fmt', 'yuv420p',
       '-vf', 'scale=in_range=full:out_range=tv:out_color_matrix=bt709', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
       '-color_range', 'tv', '-movflags', '+faststart', 'scentro_women_reel_v4_silent.mp4']
p = subprocess.Popen(cmd, stdin=subprocess.PIPE); rng = np.random.default_rng(4)
for n in range(NF):
    t = n / FPS
    if t >= MONTAGE_END + XF: f = cta_frame(t)
    elif t >= MONTAGE_END:                                                      # the only dissolve: last perfume -> plain CTA background
        k = ease((t - MONTAGE_END) / XF); f = (1 - k) * view(len(ORDER) - 1, MONTAGE_END) + k * cta_frame(t, text_on=False)
    else:
        i = max(j for j in range(len(ORDER)) if BOUNDS[j] <= t + 1e-9); f = view(i, t)       # hard cut at each boundary
    f = cv2.resize(f, (WO, HO), interpolation=cv2.INTER_AREA)
    f += rng.normal(0, 0.6, f.shape[:2])[..., None]
    p.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
    if n % 60 == 0: print(f'frame {n}/{NF}', flush=True)
p.stdin.close(); p.wait(); print('done', NF, 'frames', round(total, 2), 's')
