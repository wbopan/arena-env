## Reference notes

Use Python’s standard-library `wave` and `json`, plus NumPy. The WAV is already extracted; no video or audio extraction step is needed. The supplied pause-detector CLI defaults to a **30-second** context and produces a different JSON schema, so implement the task’s specified 15-second centered context directly.

```python
import wave
import numpy as np

with wave.open("/root/work/lecture_audio.wav", "rb") as wav:
    rate = wav.getframerate()       # read; do not assume 16000
    channels = wav.getnchannels()
    width = wav.getsampwidth()
    frames = wav.readframes(wav.getnframes())

# For mono, 16-bit signed PCM: width == 2, channels == 1.
samples = np.frombuffer(frames, dtype="<i2")
N = len(samples) // rate
full_seconds = samples[:N * rate].reshape(N, rate)
# Convert BEFORE squaring: squaring int16 values can overflow.
energies = np.sqrt(np.mean(full_seconds.astype(np.float64) ** 2, axis=1))
```

For each index `i`, average `energies[max(0, i-7):min(N, i+8)]`. Python’s slice end is exclusive, hence `i+8`. Mark low only when `energies[i] < 0.5 * local_average` (strict inequality). Group adjacent low indices into maximal runs; retain lengths ≥ 2. A run covering indices `start` through `end-1` has `duration = end - start`. Flush a run still open at index `N`.

Write `/root/work/pauses.json` with `json.dump(...)`: `audio_duration_seconds` is **N**, not the WAV’s possibly fractional duration; include only `audio_duration_seconds`, `segments`, `total_segments`, and `total_duration_seconds`. Check the written JSON and that segment starts are ordered.
