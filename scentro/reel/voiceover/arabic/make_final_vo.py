"""Final Arabic narration for Reel v2: ONE uncut ElevenLabs take (Layla, eleven_v4), no stretching / pitch change.
Adds only: 0.4 s lead-in, 15 ms fade-in, 40 ms fade-out, high-pass 75 Hz, 2-pass loudnorm (-16 LUFS, -1.5 dBTP), silence padding to 19.2 s.
Usage: python3 make_final_vo.py raw.mp3 out.wav"""
import sys, subprocess, json, numpy as np, soundfile as sf
src, out = sys.argv[1], sys.argv[2]; SR = 44100; START = 0.40; TOTAL = float(sys.argv[3]) if len(sys.argv) > 3 else 19.2
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-ac', '1', '-ar', str(SR), '/tmp/_fin_raw.wav'], check=True)
x, _ = sf.read('/tmp/_fin_raw.wav', dtype='float32')
a = int(0.0 * SR); seg = x.copy(); n1, n2 = int(0.015 * SR), int(0.040 * SR)
seg[:n1] *= np.linspace(0, 1, n1); seg[-n2:] *= np.linspace(1, 0, n2)
buf = np.zeros(int(TOTAL * SR), np.float32); i = int(START * SR); buf[i:i + len(seg)] = seg[:len(buf) - i]
sf.write('/tmp/_fin_placed.wav', buf, SR)
chain = 'highpass=f=75'
m = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', '/tmp/_fin_placed.wav', '-af', chain + ',loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex('{'):])
ln = f"loudnorm=I=-16:TP=-1.5:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '/tmp/_fin_placed.wav', '-af', f'{chain},{ln},aresample=48000,apad=whole_dur={TOTAL},atrim=0:{TOTAL}', '-ac', '2', '-c:a', 'pcm_s16le', out], check=True)
print(f'voice {START:.2f}-{START + len(seg) / SR:.2f} s of {TOTAL} s ->', out)
