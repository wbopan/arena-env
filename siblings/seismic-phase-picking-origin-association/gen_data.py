import csv
import random
from pathlib import Path

random.seed(19047)
root = Path.cwd()
stations = ['ALFA', 'BETA', 'GAMM', 'KAPPA', 'ZETA']
origin = random.randint(18, 39)
distances = random.sample([6, 12, 18, 24, 30, 36, 42], len(stations))
with (root / 'stations.csv').open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['station', 'distance_km'])
    w.writerows(zip(stations, distances))
rows = []
for i, (station, distance) in enumerate(zip(stations, distances)):
    for phase, travel in [('P', distance * 10 // 6), ('S', distance * 10 // 3)]:
        true_pick = origin + travel
        offset = (9 + 3 * i) if phase == 'P' else (13 + 2 * i)
        rows.extend([(station, phase, true_pick), (station, phase, true_pick + offset)])
random.shuffle(rows)
with (root / 'candidates.csv').open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['station', 'phase', 'pick_idx'])
    w.writerows(rows)
