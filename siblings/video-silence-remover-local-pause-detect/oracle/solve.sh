#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_pauses.py <<'EOF'
import json
import wave
import numpy as np

with wave.open("lecture_audio.wav", "rb") as w:
    sr = w.getframerate()
    raw = w.readframes(w.getnframes())
x = np.frombuffer(raw, dtype="<i2").astype(np.float64)
n = len(x) // sr
e = np.sqrt((x[: n * sr].reshape(n, sr) ** 2).mean(axis=1))
low = [e[i] < 0.5 * e[max(0, i - 7):min(n, i + 8)].mean() for i in range(n)]
segs = []
i = 0
while i < n:
    if low[i]:
        j = i
        while j < n and low[j]:
            j += 1
        if j - i >= 2:
            segs.append({"start": i, "end": j, "duration": j - i})
        i = j
    else:
        i += 1
out = {
    "audio_duration_seconds": n,
    "segments": segs,
    "total_segments": len(segs),
    "total_duration_seconds": sum(s["duration"] for s in segs),
}
with open("pauses.json", "w") as f:
    json.dump(out, f, indent=2)
EOF
python3 /tmp/solve_pauses.py
