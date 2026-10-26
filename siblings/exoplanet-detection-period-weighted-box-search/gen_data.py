import csv
import math
import random

random.seed(4107)
with open('trials.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['period_days', 'duration_days'])
    w.writerows([('2.10', '0.21'), ('2.80', '0.21'), ('3.37', '0.21'), ('4.13', '0.21')])

with open('lightcurve.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['time_days', 'flux', 'reference', 'quality', 'sigma'])
    for i in range(256):
        t = 0.07 * i
        ref = 1 + 0.014 * math.sin(2 * math.pi * t / 5.8) + 0.003 * math.cos(2 * math.pi * t / 9.1)
        phase = (t - 0.49 + 1.4) % 2.8 - 1.4
        dip = 0.024 if abs(phase) <= 0.105 else 0
        sigma = 0.0009 + (i % 5) * 0.00008
        flux = ref * (1 - dip + random.gauss(0, sigma))
        quality = 1 if i % 47 == 20 else 0
        w.writerow([f'{t:.5f}', f'{flux:.8f}', f'{ref:.8f}', quality, f'{sigma:.6f}'])
