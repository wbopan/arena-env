import csv
import random

random.seed(8031)
years = list(range(2000, 2033))
air = {y: 11 + random.gauss(0, 2.1) for y in years}
wind = {y: 4 + random.gauss(0, 0.9) for y in years}
inflow = {y: 68 + random.gauss(0, 13) for y in years}
developed = {y: 21 + 0.13 * (y - 2000) + random.gauss(0, 1.5) for y in years}
water = {2000: 10.0}
for y in years[1:]:
    heat_change = air[y - 1] - air[y - 2] if y >= 2002 else 0
    flow_change = inflow[y] - inflow[y - 1]
    water[y] = water[y - 1] + 0.32 * heat_change + 0.026 * flow_change + random.gauss(0, 0.25)

def save(path, fields, sources):
    shuffled = years[:]
    random.shuffle(shuffled)
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Year'] + fields)
        for y in shuffled:
            writer.writerow([y] + [f'{source[y]:.6f}' for source in sources])

save('water_temperature.csv', ['WaterTemp'], [water])
save('climate.csv', ['AirTemp', 'WindSpeed'], [air, wind])
save('hydrology.csv', ['Inflow'], [inflow])
save('land_cover.csv', ['DevelopedPct'], [developed])
