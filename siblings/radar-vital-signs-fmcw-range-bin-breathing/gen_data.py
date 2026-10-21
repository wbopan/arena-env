import json
import numpy as np

rng = np.random.default_rng(20240607)
N = 32
F = 128
FR = 4.0
RPB = 0.08
SCALE = 1.0 / 1024.0

win = [k for k in range(N) if 0.3 <= k * RPB <= 1.5]
n = np.arange(N)
t = np.arange(F) / FR

for i in range(1, 5):
    sub_bin = int(rng.integers(5, 18))
    cands = [k for k in win if abs(k - sub_bin) >= 2]
    stat_bin = int(cands[rng.integers(0, len(cands))])
    far_bin = int(rng.integers(22, 31))
    br_bpm = float(rng.uniform(8.0, 22.0))
    hr_hz = float(rng.uniform(1.0, 1.6))
    phi = 1.0 * np.sin(2 * np.pi * br_bpm / 60.0 * t + rng.uniform(0, 2 * np.pi)) \
        + 0.05 * np.sin(2 * np.pi * hr_hz * t)
    th = rng.uniform(0, 2 * np.pi, size=4)
    sig = np.zeros((F, N), dtype=complex)
    sig += 3000.0 * np.exp(1j * th[0])
    sig += 1000.0 * np.exp(1j * (2 * np.pi * stat_bin * n / N + th[1]))[None, :]
    sig += 1500.0 * np.exp(1j * (2 * np.pi * far_bin * n / N + th[2]))[None, :]
    sig += 200.0 * np.exp(1j * (2 * np.pi * sub_bin * n[None, :] / N + phi[:, None] + th[3]))
    sig += rng.normal(0, 20, size=(F, N)) + 1j * rng.normal(0, 20, size=(F, N))
    out = np.empty((F, N, 2), dtype='<i2')
    out[:, :, 0] = np.clip(np.round(sig.real), -32767, 32767)
    out[:, :, 1] = np.clip(np.round(sig.imag), -32767, 32767)
    out.tofile(f'cap_{i:02d}.bin')
    meta = {
        'radar_type': 'FMCW',
        'carrier_frequency_hz': 60e9,
        'format': 'int16_le_interleaved_complex',
        'scale_factor': SCALE,
        'n_frames': F,
        'chirps_per_frame': 1,
        'samples_per_chirp': N,
        'frame_rate_hz': FR,
        'range_per_bin_m': RPB,
        'duration_s': F / FR,
    }
    with open(f'cap_{i:02d}.json', 'w') as fh:
        json.dump(meta, fh, indent=2)
