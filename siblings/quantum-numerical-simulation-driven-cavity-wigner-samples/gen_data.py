import csv
import random

random.seed(24019)
with open('cavity_cases.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['case_id', 'detuning', 'drive', 'kappa', 'n_thermal'])
    for i in range(3):
        w.writerow([f'C{i+1}', round(random.uniform(-0.65, 0.8), 6), round(random.uniform(0.12, 0.48), 6), round(random.uniform(0.65, 1.35), 6), round(random.uniform(0.02, 0.3), 6)])
with open('phase_points.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['point_id', 'x', 'p'])
    for i in range(11):
        w.writerow([f'P{i+1:02}', round(random.uniform(-1.35, 1.35), 6), round(random.uniform(-1.35, 1.35), 6)])
