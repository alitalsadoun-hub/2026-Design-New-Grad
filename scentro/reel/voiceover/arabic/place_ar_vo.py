"""Place the three Layla lines (cut at their natural pauses, voice untouched - no stretching) on the Reel v2 timeline.
Usage: python3 place_ar_vo.py take.mp3 out.mp3
Cut points / onsets come from ffmpeg silencedetect on the ElevenLabs take."""
import sys, subprocess, json, numpy as np, soundfile as sf
src, out = sys.argv[1], sys.argv[2]; SR = 44100
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-ac', '1', '-ar', str(SR), '/tmp/_take.wav'], check=True)
x, _ = sf.read('/tmp/_take.wav', dtype='float32')
# natural pause centres (s) between lines + speech onsets / end, measured on this take
CUT1, CUT2 = 3.28, 7.00              # centres of the 3.06-3.50 and 6.78-7.23 pauses
ON = [0.083, 3.50, 7.23]; END = 9.55  # onset of each line, end of last line
CUES = [0.40, 6.30, 12.50]           # where each line's speech starts on the Reel timeline (s)
segs = [(0.0, CUT1), (CUT1, CUT2), (CUT2, END + 0.05)]
total = CUES[2] + (END - ON[2]) + 0.35
buf = np.zeros(int(total * SR), np.float32)
for (a, b), on, cue in zip(segs, ON, CUES):
    s = x[int(a * SR):int(b * SR)].copy(); n = int(0.02 * SR); s[:n] *= np.linspace(0, 1, n); s[-n:] *= np.linspace(1, 0, n)
    i = int((cue - (on - a)) * SR); buf[i:i + len(s)] += s
sf.write('/tmp/_placed.wav', buf, SR)
chain = 'highpass=f=75'
m = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', '/tmp/_placed.wav', '-af', chain + ',loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex('{'):])
ln = f"loudnorm=I=-16:TP=-1.5:LRA=7:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '/tmp/_placed.wav', '-af', f'{chain},{ln},aresample=48000', '-ac', '2', '-c:a', 'libmp3lame', '-b:a', '192k', out], check=True)
print(f'lines start at {CUES}, speech ends at {CUES[2] + END - ON[2]:.2f} s, file length {total:.2f} s ->', out)
