import csv
import random

random.seed(928)
sites = [(f'S{i}', random.choice([2, 3, 4])) for i in range(1, 5)]
with open('stations.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['station_id', 'response'])
    w.writerows(sites)
origins = [random.randint(7, 10), random.randint(30, 33)]
rows = []
for i, (sid, response) in enumerate(sites):
    for channel, speed in [('Z', 6), ('E', 3)]:
        values = [random.choice([-0.2, -0.1, 0, 0.1, 0.2]) * response for _ in range(48)]
        for origin in origins:
            start = origin + (i * 6) // speed
            values[start] = round(response * random.uniform(7, 9), 2)
            values[start + 1] = round(response * random.uniform(9, 12), 2)
        artifact = 2 if channel == 'Z' else 45
        values[artifact] = response * 5
        for sample, counts in enumerate(values):
            rows.append((sid, channel, sample, f'{counts:.2f}'))
random.shuffle(rows)
with open('waveforms.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['station_id', 'channel', 'sample', 'counts'])
    w.writerows(rows)
