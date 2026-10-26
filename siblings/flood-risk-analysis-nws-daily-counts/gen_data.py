import csv
import random

random.seed(1842)
ids = [f'04120{i:03d}' for i in range(1, 8)]
with open('nws_gauges.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['usgs id', 'flood stage'])
    for i, sid in enumerate(ids):
        stage = -9999 if i == 6 else 8 + i * 0.6
        w.writerow([sid, stage, 'unused export field'])
with open('gage_height_iv.rdb', 'w') as f:
    f.write('# Generated instantaneous gage heights in feet\n')
    f.write('agency_cd\tsite_no\tdatetime\t00065\t00065_cd\n')
    f.write('5s\t15s\t16d\t10n\t4s\n')
    for i, sid in enumerate(ids):
        stage = 8 + i * 0.6
        for day in range(10, 16):
            offset = random.choice([-1.5, -0.7, -0.2, 0.3, 1.1])
            for hour in (6, 12, 18):
                value = stage + offset + random.uniform(-0.18, 0.18)
                text = '' if (i == 2 and day == 12 and hour == 12) else f'{value:.3f}'
                f.write(f'USGS\t{sid}\t2025-05-{day:02d} {hour:02d}:00\t{text}\tA\n')
    f.write('USGS\t09999999\t2025-05-11 12:00\t50.0\tA\n')
