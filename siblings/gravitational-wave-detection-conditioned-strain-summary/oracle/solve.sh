#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_conditioned.py <<'PY'
import json
import numpy as np
from scipy.signal import butter, sosfiltfilt, resample_poly

x = np.load('/root/work/raw_strain.npy')
sos = butter(4, 35, fs=1024, btype='highpass', output='sos')
y = resample_poly(sosfiltfilt(sos, x), 1, 2)[64:-64]
rms = [round(float(np.sqrt(np.mean(b*b))), 6) for b in np.split(y, 4)]
i = int(np.argmax(np.abs(y)))
with open('/root/work/conditioned_summary.json', 'w') as f:
    json.dump({'sample_rate_hz': 512, 'samples': len(y), 'block_rms': rms,
               'peak_index': i, 'peak_abs': round(float(abs(y[i])), 6)}, f)
PY
python /tmp/solve_conditioned.py
