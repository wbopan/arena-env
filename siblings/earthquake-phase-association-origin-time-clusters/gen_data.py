import csv
import math
import random

random.seed(417)
stations = [(f'S{i}', float(x), float(y)) for i, (x, y) in enumerate([(0, 0), (6, 3), (12, -2), (18, 1)], 1)]
with open('stations.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['station_id', 'x_km', 'y_km'])
    w.writerows(stations)
rows = []
for origin in (random.randint(90, 105), random.randint(165, 180)):
    for sid, x, y in stations:
        distance = math.sqrt((x - 9)**2 + y*y + 6**2)
        for phase, velocity in [('p', 6), ('s', 3)]:
            rows.append((sid, phase, f'{origin + distance / velocity + random.uniform(-0.035, 0.035):.5f}', '0.95'))
for _ in range(7):
    rows.append((random.choice(stations)[0], random.choice(['p', 's']), f'{random.uniform(25, 220):.5f}', '0.30'))
random.shuffle(rows)
with open('picks.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['station_id', 'phase', 'time_s', 'prob'])
    w.writerows(rows)
