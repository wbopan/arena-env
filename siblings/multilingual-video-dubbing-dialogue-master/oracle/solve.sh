#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_dialogue_master.py <<'PY'
import wave
import numpy as np
from pathlib import Path

root = Path('/root/work')
with wave.open(str(root / 'dialogue.wav'), 'rb') as src:
    rate = src.getframerate()
    n = src.getnframes()
    channels = np.frombuffer(src.readframes(n), dtype='<i2').reshape(n, 2)
x = channels.astype(np.float64).mean(axis=1) / 32768.0
rms = np.sqrt(np.mean(np.square(x[np.abs(x) >= 0.015])))
gain = min(0.1 / rms, 10 ** (-3 / 20) / np.max(np.abs(x)))
y = x * gain
ramp = np.arange(80, dtype=np.float64) / 80
y[:80] *= ramp
y[-80:] *= ramp[::-1]
encoded = np.clip(np.rint(y * 32768), -32768, 32767).astype('<i2')
with wave.open(str(root / 'mastered.wav'), 'wb') as dst:
    dst.setparams((1, 2, rate, n, 'NONE', 'not compressed'))
    dst.writeframes(encoded.tobytes())
PY
python /tmp/solve_dialogue_master.py
