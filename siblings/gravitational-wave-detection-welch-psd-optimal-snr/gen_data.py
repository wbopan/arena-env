import numpy as np

rng = np.random.default_rng(7319)
fs = 1024
N = 4096
f = np.fft.rfftfreq(N, 1.0 / fs)
fc = np.maximum(f, 5.0)
shape = np.sqrt((30.0 / fc) ** 4 + 1.0 + (fc / 300.0) ** 2)
w = rng.normal(size=N)
x = np.fft.irfft(np.fft.rfft(w) * shape, n=N)
t = np.arange(N) / fs
fl = float(rng.choice(np.arange(50, 302, 2)))
x = x + rng.uniform(2.0, 4.0) * np.sin(2 * np.pi * fl * t + rng.uniform(0, 2 * np.pi))
np.save("strain.npy", x.astype(np.float32))

f0 = rng.uniform(25, 35)
f1 = rng.uniform(150, 250)
L = fs
tt = np.arange(L) / fs
freq = f0 + (f1 - f0) * tt ** 2
phase = 2 * np.pi * np.cumsum(freq) / fs
seg = rng.uniform(0.05, 0.15) * np.hanning(L) * np.sin(phase)
h = np.zeros(N)
start = int(rng.uniform(1.0, 2.5) * fs)
h[start:start + L] = seg
np.save("template.npy", h.astype(np.float32))
