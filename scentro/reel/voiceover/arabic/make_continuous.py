"""Continuous (uncut) Layla narration: the raw ElevenLabs take as recorded, with only the lead-in / tail trimmed so speech starts at START s.
No stretching, no pitch change, no cuts between lines (the take's own 0.27 / 0.44 / 0.45 s pauses are kept).
Usage: python3 make_continuous.py raw_take.mp3 out.mp3"""
import sys, subprocess, json, numpy as np, soundfile as sf
src, out = sys.argv[1], sys.argv[2]; SR = 44100; START = 0.40
ON, END = 0.083, 9.55                       # first / last audible time in the raw take (silencedetect, -42 dB)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-ac', '1', '-ar', str(SR), '/tmp/_raw.wav'], check=True)
x, _ = sf.read('/tmp/_raw.wav', dtype='float32')
a, b = int((ON - 0.05) * SR), int((END + 0.10) * SR)           # keep 50 ms before first sound, 100 ms after last
seg = x[a:b].copy(); n = int(0.01 * SR); seg[:n] *= np.linspace(0, 1, n); seg[-n:] *= np.linspace(1, 0, n)
lead = int((START - 0.05) * SR); buf = np.concatenate([np.zeros(lead, np.float32), seg, np.zeros(int(0.15 * SR), np.float32)])
sf.write('/tmp/_cont.wav', buf, SR)
chain = 'highpass=f=75'
m = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', '/tmp/_cont.wav', '-af', chain + ',loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex('{'):])
ln = f"loudnorm=I=-16:TP=-1.5:LRA=7:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '/tmp/_cont.wav', '-af', f'{chain},{ln},aresample=48000', '-ac', '2', '-c:a', 'libmp3lame', '-b:a', '192k', out], check=True)
print('speech starts', START, 's; file length %.2f s ->' % (len(buf) / SR), out)
