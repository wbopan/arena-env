import numpy as np

rng = np.random.default_rng(20240501)

# (dt, onset seconds or None, relative amplitude)
specs = [
    (0.01, 7.3, 6.0),
    (0.01, None, 0.0),
    (0.02, 12.5, 5.0),
    (0.01, 9.1, 1.0),
    (0.02, 16.8, 7.0),
    (0.01, 6.4, 4.0),
    (0.02, 8.9, 3.5),
    (0.01, 10.2, 8.0),
]

for i, (dt, on, amp) in enumerate(specs):
    N = 1200
    s0 = rng.uniform(0.5, 3.0)
    data = rng.normal(0.0, s0, size=(N, 3))  # columns E, N, Z
    if on is not None:
        i0 = int(round(on / dt))
        env = np.zeros(N)
        env[i0:] = np.exp(-np.arange(N - i0) * dt / 2.0)
        ev = rng.normal(0.0, 1.0, size=(N, 3)) * env[:, None] * amp * s0
        ev[:, 0] *= 0.6
        ev[:, 1] *= 0.6
        data += ev
    data += rng.uniform(-40.0, 40.0, size=3) * s0
    names = ["HHE", "HHN", "HHZ"]
    perm = [int(p) for p in rng.permutation(3)]
    data = data[:, perm]
    chans = ",".join(names[j] for j in perm)
    np.savez(f"trace_{i:02d}.npz", data=data.astype(np.float32),
             dt=np.float64(dt), channels=np.array(chans))
