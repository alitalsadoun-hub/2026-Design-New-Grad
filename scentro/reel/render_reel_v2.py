"""SCENTRO women's Reel v2 (faster, ~19 s): true 1080x1920 @30fps, H.264, silent.
One global camera path with a keyframe per clip (varied zoom / gentle pan) - both slides in a dissolve share the same camera,
so headers stay locked (no ghosted text). Frames are supersampled at 2160x3840 then area-downscaled to 1080x1920."""
import subprocess, numpy as np, cv2
from scipy.interpolate import PchipInterpolator
import cta_layers
ORDER = ['k102', 'w213', 'a118', 'y104', 'a113', 'b103', 'g102', 'b105', 'b107', 'd116']       # Kayali + Black Opium first
FPS, D, O, XF, CTA_LEN = 30, 2.0, 0.4, 0.6, 3.4
WS, HS, WO, HO = 2160, 3840, 1080, 1920
step = D - O; main_end = len(ORDER) * D - (len(ORDER) - 1) * O                  # 16.4 s of perfumes
cs = main_end - XF; total = cs + CTA_LEN; NF = round(total * FPS)                # 19.2 s total, CTA solo = 2.8 s
IVORY = np.array([228, 238, 245], np.float32)
ease = lambda x: 0.5 - 0.5 * np.cos(np.pi * np.clip(x, 0, 1))
plates = {c: cv2.imread(f'plate_{c}.png') for c in ORDER}
# camera keyframes (zoom, dx, dy in 1080x1920 plate px) at start, each clip centre, and end: alternating push-ins / wide drifts
KEYS = [(1.03, 0, 0), (1.07, 20, 25), (1.03, -10, 0), (1.10, -25, 40), (1.05, 25, 10), (1.11, 30, 45),
        (1.03, 0, -5), (1.09, -30, 40), (1.05, 15, 5), (1.10, 30, 40), (1.04, 0, 0), (1.04, 0, 0)]
KT = [0] + [i * step + D / 2 for i in range(len(ORDER))] + [main_end]
cam = [PchipInterpolator(KT, [k[j] for k in KEYS]) for j in range(3)]

def view(code, t):
    t = min(max(t, 0), main_end); z, dx, dy = (float(c(t)) for c in cam)
    mx, my = 540 * (1 - 1 / z) * 0.95, 960 * (1 - 1 / z) * 0.95                  # never pan past the plate edge
    dx, dy = float(np.clip(dx, -mx, mx)), float(np.clip(dy, -my, my))
    s = 2.0 * z; cx, cy = 540 + dx, 960 + dy
    M = np.array([[s, 0, -s * cx + WS / 2], [0, s, -s * cy + HS / 2]], np.float32)
    return cv2.warpAffine(plates[code], M, (WS, HS), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)

CTA_BG = cv2.cvtColor(np.asarray(cta_layers.background()), cv2.COLOR_RGB2BGR).astype(np.float32)
CTA_L = []
for im, cx, cy, dl in cta_layers.layers():
    a = np.asarray(im).astype(np.float32); CTA_L.append((a[..., :3][..., ::-1], a[..., 3:] / 255.0, cx - im.width // 2, cy - im.height // 2, dl))
def cta_frame(t):
    f = CTA_BG.copy(); tt = t - cs - 0.35
    for rgb, al, x, y, dl in CTA_L:
        k = float(ease((tt - dl * 0.7) / 0.5))                                    # slightly quicker stagger than v1
        if k <= 0: continue
        y2 = y + int(round((1 - k) * 22)); h, w = al.shape[:2]; a = al * k
        f[y2:y2 + h, x:x + w] = f[y2:y2 + h, x:x + w] * (1 - a) + rgb * a
    return f

cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{WO}x{HO}', '-r', str(FPS), '-i', '-',
       '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '12', '-profile:v', 'high', '-level', '4.2', '-pix_fmt', 'yuv420p',
       '-vf', 'scale=in_range=full:out_range=tv:out_color_matrix=bt709', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
       '-color_range', 'tv', '-movflags', '+faststart', 'scentro_women_reel_v2_1080p.mp4']
p = subprocess.Popen(cmd, stdin=subprocess.PIPE); rng = np.random.default_rng(2)
for n in range(NF):
    t = n / FPS
    act = [i for i in range(len(ORDER)) if i * step <= t < i * step + D]
    if t >= cs + XF: f = cta_frame(t)
    elif t >= cs: k = ease((t - cs) / XF); f = (1 - k) * view(ORDER[act[-1]], t) + k * cta_frame(t)
    elif len(act) == 1: f = view(ORDER[act[0]], t)
    else: a, b = act[0], act[1]; k = ease((t - b * step) / O); f = (1 - k) * view(ORDER[a], t) + k * view(ORDER[b], t)
    if t < 0.5: f = IVORY + (f - IVORY) * ease(t / 0.5)
    f = cv2.resize(f, (WO, HO), interpolation=cv2.INTER_AREA)
    f += rng.normal(0, 0.6, f.shape[:2])[..., None]
    p.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
    if n % 60 == 0: print(f'frame {n}/{NF}', flush=True)
p.stdin.close(); p.wait(); print('done', NF, 'frames', round(total, 2), 's')
