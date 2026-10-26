#!/usr/bin/env bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_motion.py <<'PY'
import json
import numpy as np

results = []
for j in range(1, 4):
    name = f'motion_{j:02d}'
    with open(name + '.json') as f:
        m = json.load(f)
    a = np.fromfile(name + '.bin', dtype='<f4')
    z = a[::2].astype(float) + 1j * a[1::2].astype(float)
    phase = np.unwrap(np.angle(z - np.mean(z)))
    t = np.arange(m['sample_count']) / m['sample_rate_hz']
    slope, intercept = np.polyfit(t, phase, 1)
    displacement = (phase - slope * t - intercept) * (299792458 / m['carrier_frequency_hz']) * 1000 / (4 * np.pi)
    results.append({'capture_id': name, 'rms_displacement_mm': round(float(np.sqrt(np.mean(displacement ** 2))), 3), 'peak_to_peak_mm': round(float(np.max(displacement) - np.min(displacement)), 3)})
with open('motion_summary.json', 'w') as f:
    json.dump(results, f)
PY
python /tmp/solve_motion.py
