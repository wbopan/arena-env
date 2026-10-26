import csv
import math
import random

random.seed(603)
stations = [('AA', 0, 0), ('BB', 8, 2), ('CC', 15, -3), ('DD', 22, 1)]
events = [(f'E{i}', float(random.randint(30, 40) + 65*i), float(random.choice([4, 9, 14])), float(random.choice([-2, 3])), 5.0) for i in range(3)]
with open('stations.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['station_id', 'x_km', 'y_km']); w.writerows(stations)
with open('events.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['event_id', 'time_s', 'x_km', 'y_km', 'depth_km']); w.writerows(events)
offsets = {sid: random.uniform(-0.8, 0.8) for sid, _, _ in stations}
rows = []
for sid, x, y in stations:
    for eid, t, ex, ey, depth in events:
        arrival = t + math.sqrt((x-ex)**2 + (y-ey)**2 + depth**2)/6 + offsets[sid]
        rows.append((sid, 'BHZ', f'{arrival + random.uniform(-.035,.035):.5f}', '0.94'))
        rows.append((sid, 'HHZ', f'{arrival + random.uniform(.12,.25):.5f}', '0.83'))
rows.extend([('BB', 'EHZ', '13.4', '0.99'), ('CC', 'BHZ', '18.2', '0.25')])
random.shuffle(rows)
with open('picks.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['station_id', 'channel', 'time_s', 'prob']); w.writerows(rows)
