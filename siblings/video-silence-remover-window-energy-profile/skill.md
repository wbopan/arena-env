## Reference notes

Use Python’s standard-library `wave` and `json` modules with `numpy`; no audio extraction or silence-detection step is needed. The energy-calculator CLI supports `--window-seconds 0.5`, but direct calculation gives control over the required rounding and statistics.

```python
import wave
import numpy as np

with wave.open("/root/work/lecture_audio.wav", "rb") as wav:
    rate = wav.getframerate()          # read from the header
    n = wav.getnframes()
    assert wav.getnchannels() == 1 and wav.getsampwidth() == 2
    samples = np.frombuffer(wav.readframes(n), dtype="<i2").astype(np.float64)
```

`<i2` decodes little-endian signed 16-bit PCM. Convert to `float64` **before squaring** to avoid integer overflow. For each consecutive half-second window starting at sample zero, include its available samples even when the last window is short:

```python
rms = float(np.sqrt(np.mean(window * window)))
```

Keep the RMS values unrounded while computing `min`, `max`, `mean`, and population standard deviation (`np.std(values, ddof=0)`). Then round each energy and statistic to three decimal places. Set `total_seconds` to `len(energies) * 0.5`, not the WAV’s exact duration. Write a JSON object with only the specified top-level fields and only the specified four `stats` fields; convert NumPy scalars to ordinary Python numbers for `json.dump`.
