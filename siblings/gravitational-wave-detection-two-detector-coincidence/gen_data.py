import csv
import random

random.seed(8675309)


def catalog(prefix, count):
    rows = []
    for i in range(count):
        rows.append({'trigger_id': f'{prefix}{i:02d}',
                     'time_s': round(100 + i * 0.137 + random.uniform(-0.025, 0.025), 6),
                     'snr': round(random.uniform(4.0, 10.0), 4),
                     'total_mass_solar': round(random.uniform(24, 73), 4)})
    return rows

h = catalog('H', 18)
l = catalog('L', 18)
# Plant several plausible coincidences and loud, deliberately incompatible triggers.
h[4].update(time_s=101.101203, snr=10.83, total_mass_solar=48.7)
l[12].update(time_s=101.109614, snr=11.19, total_mass_solar=49.8)
h[9].update(time_s=102.432178, snr=12.26, total_mass_solar=62.3)
l[2].update(time_s=102.427920, snr=8.81, total_mass_solar=63.4)
h[16].update(time_s=103.219104, snr=17.4, total_mass_solar=37.0)
l[17].update(time_s=103.220703, snr=6.4, total_mass_solar=56.0)
for filename, rows in [('hanford_triggers.csv', h), ('livingston_triggers.csv', l)]:
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['trigger_id', 'time_s', 'snr', 'total_mass_solar'])
        writer.writeheader()
        writer.writerows(rows)
