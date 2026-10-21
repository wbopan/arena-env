#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import json
import numpy as np
from scipy.signal import welch

rows = []
for i in range(1, 5):
    cid = f'cap_{i:02d}'
    meta = json.load(open(f'{cid}.json'))
    raw = np.fromfile(f'{cid}.bin', dtype='<i2').astype(np.float64) * meta['scale_factor']
    iq = raw[0::2] + 1j * raw[1::2]
    F, N = meta['n_frames'], meta['samples_per_chirp']
    R = np.fft.fft(iq.reshape(F, N), axis=1)
    R -= R.mean(axis=0, keepdims=True)
    mag = np.abs(R).mean(axis=0)
    rpb = meta['range_per_bin_m']
    ks = [k for k in range(N) if 0.3 - 1e-9 <= k * rpb <= 1.5 + 1e-9]
    best = ks[int(np.argmax(mag[ks]))]
    ph = np.unwrap(np.angle(R[:, best]))
    ph -= ph.mean()
    fs = meta['frame_rate_hz']
    f, p = welch(ph, fs=fs, nperseg=F, noverlap=F // 2, nfft=8 * F, detrend='constant')
    m = (f >= 0.08) & (f <= 0.5)
    br = f[m][int(np.argmax(p[m]))] * 60.0
    rows.append(f'{cid},{best},{best * rpb:.2f},{br:.1f}')

with open('range_results.csv', 'w') as fh:
    fh.write('capture_id,range_bin,range_m,breathing_rate_bpm\n')
    fh.write('\n'.join(rows) + '\n')
EOF
python3 /tmp/solve.py
