#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_phase.py <<'PY'
import json
import numpy as np
from scipy.signal import hilbert

x = np.load('/root/work/strain.npy')
t = np.load('/root/work/template.npy')
p = np.load('/root/work/noise_psd.npy')
xf = np.fft.rfft(x)
projections = []
for h in (t, hilbert(t).imag):
    hf = np.fft.rfft(h)
    numerator = np.fft.irfft(xf * hf.conj() / p, n=len(x))
    norm2 = np.fft.irfft(hf * hf.conj() / p, n=len(x))[0]
    projections.append(numerator / np.sqrt(norm2))
magnitudes = np.hypot(projections[0], projections[1])
lag = 128 + int(np.argmax(magnitudes[128:896]))
with open('/root/work/phase_peak.json', 'w') as f:
    json.dump({'lag_samples': lag, 'peak_snr': round(float(magnitudes[lag]), 6),
               'phase_rad': round(float(np.arctan2(projections[1][lag], projections[0][lag])), 6)}, f)
PY
python /tmp/solve_phase.py
