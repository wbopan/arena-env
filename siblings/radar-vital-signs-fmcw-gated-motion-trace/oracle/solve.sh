#!/usr/bin/env bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_gated.py <<'PY'
import csv
import json
import numpy as np

with open('gated_motion.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['capture_id', 'second', 'displacement_mm'])
    for j in (1, 2):
        name = f'sweep_{j:02d}'
        with open(name + '.json') as sidecar:
            m = json.load(sidecar)
        a = np.fromfile(name + '.bin', dtype='<i2').astype(float).reshape(m['chirp_count'], m['samples_per_chirp'])
        spectrum = np.fft.rfft(a - a.mean(axis=1, keepdims=True), axis=1)
        spectrum -= spectrum.mean(axis=0, keepdims=True)
        bins = [k for k in range(spectrum.shape[1]) if 0.3 - 1e-9 <= k * m['range_per_bin_m'] <= 0.9 + 1e-9]
        best = bins[int(np.argmax([np.abs(spectrum[:, k]).mean() for k in bins]))]
        phase = np.unwrap(np.angle(spectrum[:, best]))
        t = np.arange(m['chirp_count']) / m['chirp_rate_hz']
        slope, offset = np.polyfit(t, phase, 1)
        mm = (phase - slope * t - offset) * (299792458 / m['carrier_frequency_hz']) * 1000 / (4 * np.pi)
        for i in range(0, m['chirp_count'], m['chirp_rate_hz']):
            writer.writerow([name, i // m['chirp_rate_hz'], f'{mm[i]:.3f}'])
PY
python /tmp/solve_gated.py
