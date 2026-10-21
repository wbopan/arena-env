import json
import os
import wave

import numpy as np

rng = np.random.default_rng(31)
SR = 16000
os.makedirs("tts", exist_ok=True)


def ts(t):
    ms = int(round(t * 1000))
    return "%02d:%02d:%02d,%03d" % (ms // 3600000, (ms // 60000) % 60, (ms // 1000) % 60, ms % 1000)


blocks = []
t = 0.25
for k in range(1, 6):
    n = int(rng.integers(int(0.35 * SR), int(0.58 * SR)))
    clip_dur = n / SR
    if k in (2, 4):
        wdur = clip_dur * rng.uniform(0.65, 0.9)
    else:
        wdur = clip_dur * rng.uniform(1.15, 1.6)
    start = round(t + rng.uniform(0.2, 0.5), 3)
    end = round(start + wdur, 3)
    t = end
    tt = np.arange(n) / SR
    f0 = rng.uniform(110, 260)
    sig = (np.sin(2 * np.pi * f0 * tt) + 0.5 * np.sin(2 * np.pi * 2.03 * f0 * tt + 1.0)
           + 0.25 * np.sin(2 * np.pi * 3.1 * f0 * tt))
    env = np.abs(np.sin(np.pi * tt / tt[-1])) ** 0.5 * (0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(3, 6) * tt))
    sig = sig * env + 0.02 * rng.standard_normal(n)
    amp = rng.uniform(0.05, 0.7)
    sig = sig / np.max(np.abs(sig)) * amp
    pcm = np.round(sig * 32767).astype("<i2")
    with wave.open(os.path.join("tts", "seg_%d.wav" % k), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    blocks.append("%d\n%s --> %s\n[dub line %d]\n" % (k, ts(start), ts(end), k))

with open("segments.srt", "w", encoding="utf-8") as f:
    f.write("\n".join(blocks))
with open("timeline.json", "w") as f:
    json.dump({"sample_rate": SR, "duration_sec": round(t + 0.6, 1)}, f)
