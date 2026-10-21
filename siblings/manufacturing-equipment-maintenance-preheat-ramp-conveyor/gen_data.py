import csv
import random

import numpy as np

random.seed(77)
rng = np.random.default_rng(77)

HANDBOOK = '''# Reflow Oven Process Handbook (rev D)

## 1. Thermal profile regions
The profile is divided into preheat, soak, reflow and cooling. Preheat is the
region in which the board heats through the temperature band 100 C to 150 C.
Soak follows preheat; reflow is the region above solder liquidus.

## 2. Ramp rate guidance
Ramp rate is computed between consecutive thermocouple samples (sorted by time)
as (T_i - T_(i-1)) / (t_i - t_(i-1)); segments with non-increasing time are ignored.
A segment belongs to preheat only when both of its endpoint temperatures lie
within the preheat band (inclusive). The maximum preheat ramp rate must not
exceed 2.0 C/s.
Note: revision B allowed 3.0 C/s; that value is superseded and must not be used.

## 3. Ovens
| oven_id | zones | heated_length_cm |
|---------|-------|------------------|
| OV-A    | 8     | 360              |
| OV-B    | 10    | 420              |
| OV-C    | 7     | 300              |

## 4. Dwell requirements
Dwell time is the time a board spends inside the heated length.
Minimum dwell by board family: THIN 150 s, STD 180 s, THICK 220 s.
Maximum dwell for every family: 330 s.
'''

with open('handbook.md', 'w') as f:
    f.write(HANDBOOK)


def profile(times, L, r1, peak, hold):
    t1 = 125.0 / r1
    kt = [0.0, t1, t1 + 50.0]
    ky = [25.0, 150.0, L - 30.0]
    tp = kt[-1] + (peak - (L - 30.0)) / 1.5
    kt += [tp, tp + hold, tp + hold + (peak - 80.0) / 2.5]
    ky += [peak, peak, 80.0]
    return np.interp(times, kt, ky)


times = np.arange(0, 275, 5)
mes = []
rows = []
for i in range(1, 7):
    rid = f'R{i:02d}'
    mes.append([rid, random.choice(['THIN', 'STD', 'THICK']), random.choice(['OV-A', 'OV-B', 'OV-C']),
                round(random.uniform(55, 125), 1)])
    if rid == 'R04':
        continue
    r1 = random.uniform(1.5, 2.4)
    peak = 217.0 + random.uniform(15, 30)
    hold = random.uniform(15, 40)
    for tc in ['TC1', 'TC2', 'TC3']:
        y = profile(times, 217.0, r1 + random.uniform(-0.25, 0.25), peak + random.uniform(-5, 2), hold)
        y = y + rng.normal(0, 0.5, size=len(times))
        for t, v in zip(times, y):
            rows.append([rid, tc, int(t), round(float(v), 1)])
random.shuffle(rows)

with open('mes_log.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['run_id', 'board_family', 'oven_id', 'conveyor_speed_cm_min'])
    w.writerows(mes)

with open('thermocouples.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['run_id', 'tc_id', 'time_s', 'temp_c'])
    w.writerows(rows)
