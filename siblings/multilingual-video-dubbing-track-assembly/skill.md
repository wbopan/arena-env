## Reference notes

Use Python’s `wave` module and NumPy for sample-exact PCM processing. FFmpeg’s `loudnorm`, fades, resampling, and time-based trimming do **not** implement the specified RMS and sample rules; do not apply them.

```python
import json, re, wave
from pathlib import Path
import numpy as np

root = Path("/root/work")
meta = json.loads((root / "timeline.json").read_text())
rate = 16000
total_frames = round(meta["duration_sec"] * rate)
track = np.zeros(total_frames, dtype=np.int16)

def timestamp_samples(stamp):
    h, m, sec, ms = map(int, re.fullmatch(
        r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", stamp
    ).groups())
    # At 16 kHz, each millisecond is exactly 16 samples.
    return ((h * 3600 + m * 60 + sec) * 1000 + ms) * 16
```

SRT cues are blank-line-separated; the first line is the cue index `k`, and the next line contains `start --> end`. Use that **index**, not iteration position, to open `tts/seg_k.wav`. Split on `-->` and strip whitespace before parsing timestamps.

For each WAV, check `getnchannels() == 1`, `getsampwidth() == 2`, and `getframerate() == 16000`. Read with `readframes(getnframes())`, then decode little-endian signed PCM via `np.frombuffer(data, dtype="<i2").astype(np.float64)`. Compute RMS over the **entire decoded clip before trimming**:

```python
rms = np.sqrt(np.mean((x / 32768.0) ** 2))
gain = 0.1 / rms                 # 10**(-20/20)
s, e = timestamp_samples(start), timestamp_samples(end)
count = min(len(x), e - s)
placed = np.clip(np.rint(x[:count] * gain), -32768, 32767).astype(np.int16)
track[s:s + count] = placed
```

`np.rint` rounds to nearest integer; clipping must precede conversion to `int16`. Do not stretch clips, fill unused window space with anything but zero, or modify samples outside windows. Zero-RMS clips make the prescribed gain undefined; inspect them rather than dividing by zero.

Write with `wave.open(..., "wb")`, `setnchannels(1)`, `setsampwidth(2)`, `setframerate(16000)`, and `writeframes(track.astype("<i2").tobytes())`. After running the script, reopen the output and check its parameters and `getnframes() == total_frames`.
