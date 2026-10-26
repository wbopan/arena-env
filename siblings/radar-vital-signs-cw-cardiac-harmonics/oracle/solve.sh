#!/usr/bin/env bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_cardiac.py <<'PY'
import csv
import json
import numpy as np

with open('cardiac_rates.csv', 'w', newline='') as out:
    writer = csv.writer(out)
    writer.writerow(['capture_id', 'dominant_hr_hz', 'heart_rate_bpm'])
    for j in range(1, 4):
        name = f'pulse_{j:02d}'
        with open(name + '.json') as f:
            meta = json.load(f)
        data = np.fromfile(name + '.bin', dtype='<i2').astype(float)
        iq = data[::2] + 1j * data[1::2]
        phase = np.unwrap(np.angle(iq - iq.mean()))
        t = np.arange(len(iq)) / meta['sample_rate_hz']
        slope, offset = np.polyfit(t, phase, 1)
        phase -= slope * t + offset
        freq = np.fft.rfftfreq(len(phase), d=1 / meta['sample_rate_hz'])
        power = np.abs(np.fft.rfft(phase)) ** 2
        bins = np.where((freq >= 0.7) & (freq <= 3.0))[0]
        top = bins[np.argmax(power[bins])]
        dominant = freq[top]
        fundamental = dominant
        if 0.7 <= dominant / 2 <= 3.0 and np.interp(dominant / 2, freq, power) > power[top] / 2:
            fundamental = dominant / 2
        writer.writerow([name, f'{dominant:.4f}', f'{60 * fundamental:.1f}'])
PY
python /tmp/solve_cardiac.py
