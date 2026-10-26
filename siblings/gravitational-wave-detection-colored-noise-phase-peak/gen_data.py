import numpy as np
from scipy.signal import hilbert

rng = np.random.default_rng(271828)
n = 1024
fs = 512
t = np.arange(n) / fs
u = np.arange(n) - 110
wave = np.exp(-0.5 * (u / 48) ** 2) * np.cos(2 * np.pi * (42 * u / fs + 24 * (u / fs) ** 2))
wave = wave.astype(np.float64)
f = np.fft.rfftfreq(n, 1 / fs)
psd = 1 + 6 * (f / 256) ** 2 + 5 * np.exp(-0.5 * ((f - 119) / 7) ** 2)
noise = np.fft.irfft(np.fft.rfft(rng.normal(size=n)) * np.sqrt(psd), n=n)
phase = 0.83
strain = noise + 2.4 * np.roll(np.cos(phase) * wave + np.sin(phase) * hilbert(wave).imag, 437)
np.save('strain.npy', strain)
np.save('template.npy', wave)
np.save('noise_psd.npy', psd)
