import csv
import random

random.seed(4107)
cols = ['AirTemp', 'Radiation', 'WindSpeed', 'Inflow', 'Runoff', 'DevelopedPct', 'AgriculturePct', 'TreeCoverPct']
files = {'climate.csv': cols[:3], 'hydrology.csv': cols[3:5], 'land_cover.csv': cols[5:]}
rows = []
for year in range(1993, 2023):
    heat, flow, wind, human = (random.gauss(0, 1) for _ in range(4))
    signals = [heat, heat, wind, flow, flow, human, human, human]
    scales = [2.1, 13, 0.8, 11, 7, 2.3, 1.7, 2.0]
    bases = [13, 165, 4, 72, 38, 19, 33, 48]
    values = [round(b + s * (z + random.gauss(0, 0.23)), 5) for b, s, z in zip(bases, scales, signals)]
    rows.append(dict(Year=year, **dict(zip(cols, values)), WaterTemp=round(10 + 0.7 * heat + random.gauss(0, 0.4), 5)))
random.shuffle(rows)
for path, names in files.items():
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Year'] + names)
        writer.writeheader()
        writer.writerows({k: row[k] for k in ['Year'] + names} for row in rows)
with open('water_temperature.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Year', 'WaterTemp'])
    writer.writeheader()
    writer.writerows({k: row[k] for k in ['Year', 'WaterTemp']} for row in rows)
