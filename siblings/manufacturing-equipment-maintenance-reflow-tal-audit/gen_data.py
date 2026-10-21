import csv
import random

import numpy as np
import yaml

random.seed(2024)
rng = np.random.default_rng(2024)

ALLOYS = [
    {'name': 'SAC305', 'liquidus_c': 217.0, 'tal_min_s': 45, 'tal_max_s': 90},
    {'name': 'SN63PB37', 'liquidus_c': 183.0, 'tal_min_s': 30, 'tal_max_s': 75},
    {'name': 'SN100C', 'liquidus_c': 227.0, 'tal_min_s': 40, 'tal_max_s': 80},
]
LIQ = {a['name']: a['liquidus_c'] for a in ALLOYS}

with open('spec.yaml', 'w') as f:
    yaml.safe_dump({
        'document': 'Reflow process specification rev C',
        'tal_definition': 'time strictly above alloy liquidus, measured per thermocouple',
        'alloys': ALLOYS,
    }, f, sort_keys=False)


def profile(times, L, r1, peak, hold):
    t1 = 125.0 / r1
    kt = [0.0, t1, t1 + 50.0]
    ky = [25.0, 150.0, L - 30.0]
    tp = kt[-1] + (peak - (L - 30.0)) / 1.5
    kt += [tp, tp + hold, tp + hold + (peak - 80.0) / 2.5]
    ky += [peak, peak, 80.0]
    return np.interp(times, kt, ky)


times = np.arange(0, 275, 5)
run_ids = [f'R{i:02d}' for i in range(1, 7)]
alloy_cycle = ['SAC305', 'SN63PB37', 'SN100C', 'SAC305', 'SN100C', 'SN63PB37']
families = ['THIN', 'STD', 'THICK']
mes = []
rows = []
for i, rid in enumerate(run_ids):
    alloy = alloy_cycle[i]
    L = LIQ[alloy]
    mes.append([rid, random.choice(families), alloy, random.choice(['OV-A', 'OV-B']), round(random.uniform(60, 120), 1)])
    if rid == 'R05':
        continue
    base_peak = L + random.uniform(18, 35)
    hold = random.uniform(15, 45)
    r1 = random.uniform(1.4, 2.6)
    for tc in ['TC1', 'TC2', 'TC3']:
        pk = base_peak + random.uniform(-7, 2)
        y = profile(times, L, r1 + random.uniform(-0.2, 0.2), pk, hold + random.uniform(-5, 5))
        y = y + rng.normal(0, 0.5, size=len(times))
        for t, v in zip(times, y):
            rows.append([rid, tc, int(t), round(float(v), 1)])
random.shuffle(rows)

with open('mes_log.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['run_id', 'board_family', 'alloy', 'oven_id', 'conveyor_speed_cm_min'])
    w.writerows(mes)

with open('thermocouples.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['run_id', 'tc_id', 'time_s', 'temp_c'])
    w.writerows(rows)
