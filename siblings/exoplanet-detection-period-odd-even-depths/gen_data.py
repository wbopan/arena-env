import csv
import math
import random

random.seed(9821)
candidates = [('A', 2.45, 0.46, 0.25), ('B', 3.73, 1.19, 0.25)]
with open('candidates.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['id', 'period_days', 'epoch_days', 'duration_days'])
    for name, p, e, d in candidates:
        w.writerow([name, p, e, d])

with open('photometry.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['time_days', 'flux', 'reference', 'quality', 'sigma'])
    for i in range(360):
        t = i * 0.07
        ref = 1 + 0.012 * math.sin(t * 1.1) + 0.004 * math.cos(t * 0.43)
        dip = 0
        for name, p, e, duration in candidates:
            n = math.floor((t-e)/p + 0.5)
            if abs(t-e-n*p) <= duration/2:
                dip += (0.013 if n % 2 == 0 else 0.0125) if name == 'A' else (0.008 if n % 2 == 0 else 0.018)
        sigma = 0.00055 + (i % 4) * 0.00007
        flux = ref * (1-dip+random.gauss(0, sigma))
        quality = 2 if i % 61 == 13 else 0
        w.writerow([f'{t:.5f}', f'{flux:.8f}', f'{ref:.8f}', quality, f'{sigma:.6f}'])
