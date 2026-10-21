import numpy as np

rng = np.random.default_rng(1337)

# code, dt, P onset (s), S-P time (s)
stations = [
    ("ST01", 0.01, 2.2, 3.9),
    ("ST02", 0.02, 3.0, 6.3),
    ("ST03", 0.01, 2.8, 1.7),
    ("ST04", 0.01, 3.4, 4.6),
    ("ST05", 0.02, 4.0, 9.8),
]

for code, dt, tp, sp in stations:
    N = 1000
    s0 = rng.uniform(0.3, 2.0)
    n = np.arange(N)
    ip = int(round(tp / dt))
    isx = int(round((tp + sp) / dt))
    envP = np.where(n >= ip, np.exp(-(n - ip) * dt / 1.5), 0.0)
    envS = np.where(n >= isx, np.exp(-(n - isx) * dt / 3.0), 0.0)
    cols = {
        "Z": s0 * rng.normal(size=N) + s0 * rng.normal(size=N) * (6.0 * envP + 2.0 * envS),
        "E": s0 * rng.normal(size=N) + s0 * rng.normal(size=N) * (1.5 * envP + 10.0 * envS),
        "N": s0 * rng.normal(size=N) + s0 * rng.normal(size=N) * (1.5 * envP + 12.0 * envS),
    }
    order = [str(c) for c in rng.permutation(["E", "N", "Z"])]
    prefix = "HH" if dt == 0.01 else "BH"
    data = np.stack([cols[c] + rng.uniform(-30.0, 30.0) * s0 for c in order], axis=1)
    np.savez(f"sta_{code}.npz", data=data.astype(np.float32), dt=np.float64(dt),
             channels=np.array(",".join(prefix + c for c in order)),
             station=np.array(code))
