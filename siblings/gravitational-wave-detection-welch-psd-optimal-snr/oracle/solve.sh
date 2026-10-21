#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json
import numpy as np
from scipy.signal import welch
fs = 1024.0
x = np.load("strain.npy").astype(np.float64)
h = np.load("template.npy").astype(np.float64)
fw, P = welch(x, fs=fs, window="hann", nperseg=512, noverlap=256, detrend="constant",
              return_onesided=True, scaling="density", average="mean")
m = (fw >= 20) & (fw <= 400)
line = float(fw[m][np.argmax(P[m])])
bands = []
for lo, hi in [(20, 40), (40, 80), (80, 160), (160, 320)]:
    s = (fw >= lo) & (fw < hi)
    bands.append({"f_low": lo, "f_high": hi, "asd": float(np.sqrt(P[s].mean()))})
N = len(h)
hf = np.fft.rfft(h) / fs
ff = np.fft.rfftfreq(N, 1.0 / fs)
df = fs / N
S = np.interp(ff, fw, P)
k = (ff >= 20) & (ff <= 400)
snr = float(np.sqrt(4.0 * np.sum(np.abs(hf[k]) ** 2 / S[k]) * df))
with open("/root/work/psd_report.json", "w") as f:
    json.dump({"line_frequency_hz": line, "band_asd": bands, "optimal_snr": snr}, f, indent=2)
EOF
python3 /tmp/solve.py
