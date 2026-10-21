import csv
import numpy as np

rng = np.random.default_rng(7)
T = 240
pad = 12
x = np.zeros(T + pad)
for i in range(2, T + pad):
    x[i] = 1.6 * x[i - 1] - 0.7 * x[i - 2] + rng.normal(0, 0.004)
t = np.arange(T)
xs = x[pad:]
x2 = x[pad - 2:pad - 2 + T]
x3 = x[pad - 3:pad - 3 + T]
lip = np.log(100) + 0.0015 * t + xs + rng.normal(0, 0.002, T)
lpay = np.log(130000) + 0.0008 * t + 0.4 * x2 + rng.normal(0, 0.0006, T)
ur = 5.5 - 0.004 * t + 0.4 * np.sin(t / 30.0) - 60 * x3 + rng.normal(0, 0.06, T)
ur = np.clip(ur, 2.5, None)
rows = []
for i in range(T):
    y, m = 2005 + i // 12, i % 12 + 1
    rows.append([f"{y}-{m:02d}", f"{np.exp(lip[i]):.3f}", str(int(round(np.exp(lpay[i])))), f"{ur[i]:.1f}"])
perm = rng.permutation(T)
with open("indicators.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["month", "ip_index", "payroll_thousands", "unemployment_rate"])
    for j in perm:
        w.writerow(rows[j])
