import csv
import math
import random

random.seed(7319)
t0, period = 0.39, 2.21
with open('windows.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['event_number', 'predicted_center_days'])
    for n in range(8):
        w.writerow([n, f'{0.40 + n*2.208:.6f}'])

with open('lightcurve.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['time_days', 'flux', 'reference', 'quality'])
    for i in range(386):
        t = i * 0.045
        ref = 1 + 0.011 * math.sin(t * 0.77) + 0.003 * math.cos(t * 1.41)
        dip = 0.0
        for n in range(8):
            center = t0 + n*period + 0.014*math.sin(n*1.3)
            dip += 0.022 * max(0.0, 1-abs(t-center)/0.105)
        flux = ref * (1-dip+random.gauss(0, 0.00012))
        quality = 1 if i % 79 == 37 else 0
        w.writerow([f'{t:.6f}', f'{flux:.8f}', f'{ref:.8f}', quality])
