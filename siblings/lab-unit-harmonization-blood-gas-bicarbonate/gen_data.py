import csv
import random

random.seed(9031)

def display(value, comma, padded):
    s = f'{value:.3f}'
    if comma:
        s = s.replace('.', ',')
    return f' {s} ' if padded else s

with open('arterial_gases.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['sample_id', 'ph', 'pco2_value', 'pco2_unit', 'po2_value', 'po2_unit'])
    for i in range(16):
        ph = random.randint(715, 753) / 100
        co2 = random.randint(250, 720) / 10
        o2 = random.randint(610, 1450) / 10
        cu = 'kPa' if i % 2 else 'mmHg'
        ou = 'kPa' if i % 3 else 'mmHg'
        co2raw = co2 / 7.5 if cu == 'kPa' else co2
        o2raw = o2 / 7.5 if ou == 'kPa' else o2
        w.writerow([f'ABG-{i+1:02}', display(ph, i % 3 == 0, i % 2 == 0), display(co2raw, i % 3 == 1, i % 2 == 1), cu, display(o2raw, i % 3 == 2, i % 4 == 0), ou])
