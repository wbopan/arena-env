import csv
import random

random.seed(7713)
ids = [f'0210{i:04d}' for i in range(1, 7)]
patterns = ['00111220', '00022000', '01111111', '20000000', '00001222', '00000000']
with open('nws_gauges.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['usgs id', 'action stage', 'flood stage'])
    for i, sid in enumerate(ids):
        w.writerow([sid, f'{4 + i * 0.5:.2f}', f'{6 + i * 0.5:.2f}', 'unused'])
with open('gage_height_iv.rdb', 'w') as f:
    f.write('# Local-time instantaneous heights in feet\n')
    f.write('agency_cd\tsite_no\tdatetime\t00065\t00065_cd\n')
    f.write('5s\t15s\t16d\t10n\t4s\n')
    for i, sid in enumerate(ids):
        action = 4 + i * 0.5
        for day, code in enumerate(patterns[i], 1):
            if i == 4 and day == 3:
                continue
            for hour in (8, 20):
                offset = {'0': -0.8, '1': 0.8, '2': 2.5}[code]
                if hour == 8:
                    offset -= 0.5
                value = action + offset + random.uniform(-0.1, 0.1)
                f.write(f'USGS\t{sid}\t2025-07-{day:02d} {hour:02d}:00\t{value:.2f}\tA\n')
    f.write('USGS\t02100005\t2025-07-03 12:00\t\tA\n')
