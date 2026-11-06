"""Scentro Reel v2 voice-over: Kokoro-82M (local neural TTS, Apache-2.0) -> timed phrases -> processed mono/stereo WAV.
Usage: python3 build_vo.py VOICE LANG SPEED OUT_BASENAME   e.g.  python3 build_vo.py af_heart en-us 0.93 vo_heart
Models are expected in $KOKORO_DIR (kokoro-v1.0.onnx, voices-v1.0.bin)."""
import os, sys, subprocess, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
voice, lang, speed, base = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
KD = os.environ.get('KOKORO_DIR', '.'); SR = 24000; TOTAL = 19.2
# (text, start_time_s)  - cue times match Reel v2: CTA text appears from ~16.2 s, URL fully visible ~17.3 s
CUES = [("Your favorite fragrances...", 0.7),
        ("Reimagined.", 3.3),
        ("Discover the scents you love, at Scentro.", 5.3),
        ("Your next signature scent... is just a click away.", 10.2),
        ("Shop now at", None),                       # None = anchored so it ends 0.12 s before the next phrase
        ("Scentro, J O, dot com.", 16.95)]          # website phrase starts as the URL fades in on the end screen
k = Kokoro(os.path.join(KD, 'kokoro-v1.0.onnx'), os.path.join(KD, 'voices-v1.0.bin'))
buf = np.zeros(int(TOTAL * SR), np.float32); report = []; clips = []
for text, t0 in CUES:
    a, sr = k.create(text, voice=voice, speed=speed, lang=lang); assert sr == SR
    a = np.trim_zeros(a.astype(np.float32), 'fb'); n = int(0.03 * SR)           # 30 ms fades so phrases never click
    a[:n] *= np.linspace(0, 1, n); a[-n:] *= np.linspace(1, 0, n); clips.append((text, t0, a))
starts = [c[1] for c in clips]
for j in range(len(clips) - 1, -1, -1):
    if starts[j] is None: starts[j] = starts[j + 1] - len(clips[j][2]) / SR - 0.12
for (text, _, a), t0 in zip(clips, starts):
    i = int(t0 * SR); buf[i:i + len(a)] += a[:len(buf) - i]; report.append((t0, t0 + len(a) / SR, text))
assert all(report[j][1] <= report[j + 1][0] for j in range(len(report) - 1)), 'phrases overlap'
assert report[-1][1] < TOTAL - 0.2, 'last phrase runs past the video'

for s, e, t in report: print(f'{s:5.2f} -> {e:5.2f}  {t}')
raw = f'{base}_raw.wav'; sf.write(raw, buf, SR)
# voice-only processing: gentle high-pass, soft compression, 2-pass loudness normalisation to -16 LUFS / -1.5 dBTP, 48 kHz stereo
chain = 'highpass=f=75,lowpass=f=15000,acompressor=threshold=-21dB:ratio=2.2:attack=15:release=180:makeup=2'
m = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', raw, '-af', chain + ',loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json', '-f', 'null', '-'],
                   capture_output=True, text=True).stderr
import json; j = json.loads(m[m.rindex('{'):])
ln = (f"loudnorm=I=-16:TP=-1.5:LRA=7:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
      f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', f'{chain},{ln},aresample=48000,apad=whole_dur={TOTAL},atrim=0:{TOTAL}',
                '-ac', '2', '-c:a', 'pcm_s16le', f'{base}.wav'], check=True)
print('wrote', f'{base}.wav')
