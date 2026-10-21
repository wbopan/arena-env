#!/bin/bash
set -e
cd /root/work
cat > /tmp/assemble.py << 'EOF'
import json, wave
import numpy as np

def sec(t):
    a, ms = t.strip().split(',')
    h, m, s = a.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

tl = json.load(open('timeline.json'))
sr = int(tl['sample_rate'])
L = int(round(tl['duration_sec'] * sr))
track = np.zeros(L)
for b in open('segments.srt', encoding='utf-8').read().strip().split('\n\n'):
    ls = b.strip().split('\n')
    k = int(ls[0])
    x, y = ls[1].split('-->')
    s = int(round(sec(x) * sr))
    e = int(round(sec(y) * sr))
    with wave.open('tts/seg_%d.wav' % k, 'rb') as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float64)
    a = a * (0.1 / np.sqrt(np.mean((a / 32768.0) ** 2)))
    a = a[:e - s]
    track[s:s + len(a)] = a
pcm = np.clip(np.round(track), -32768, 32767).astype('<i2')
with wave.open('dubbed_track.wav', 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes(pcm.tobytes())
EOF
python3 /tmp/assemble.py
