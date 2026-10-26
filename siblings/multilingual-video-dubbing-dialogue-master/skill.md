## Reference notes

Use Python’s `wave` module and NumPy for frame-exact processing. FFmpeg’s `loudnorm`, `volume`, mono conversion, and time-based fades do not directly express the specified active-sample RMS, peak constraint, or per-frame fade, so avoid them for the mastering calculation.

```python
import wave
import numpy as np

with wave.open("/root/work/dialogue.wav", "rb") as w:
    channels, width, rate, frames = (
        w.getnchannels(), w.getsampwidth(),
        w.getframerate(), w.getnframes()
    )
    raw = w.readframes(frames)

# PCM WAV samples are interleaved by frame: left, right, left, right, ...
stereo = np.frombuffer(raw, dtype="<i2").reshape(-1, 2)
# Cast to float64 before arithmetic; do not average or amplify in int16.
```

- Normalize each signed PCM sample by **32768**, then average channels. Select active samples from this *unprocessed mono signal* using `abs(mono) >= 0.015`.
- Active RMS is `sqrt(mean(active**2))`; peak is `max(abs(mono))` over **all** frames. A target of `d` dBFS corresponds to linear amplitude `10**(d/20)`. Calculate each target amplitude divided by its respective measured amplitude, then use the smaller positive gain. Apply it to every frame, including inactive frames.
- Apply fades **after gain**, using frame indices rather than seconds. The first and last frames receive factor zero; at each boundary, the factor for offset `i` is `i/80` for `i = 0…79`. Do not shorten or pad the array.
- For export, `np.rint(samples * 32768)` rounds ties to even. Apply `np.clip(..., -32768, 32767)` **before** converting to `"<i2"`; casting an out-of-range value directly to int16 is not clipping.

Write with `wave.open("/root/work/mastered.wav", "wb")`, `setnchannels(1)`, `setsampwidth(2)`, `setframerate(16000)`, then `writeframes(pcm.tobytes())`. Reopen it to check mono, 16-bit, 16000 Hz, and unchanged frame count.
