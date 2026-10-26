import csv
import random

random.seed(9021)
ids = ['03310001', '03310002', '03310003', '03310004', '03310005']
patterns = ['011011101', '000110000', '101010101', '000000000', '110001100']
with open('nws_gauges.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['usgs id', 'flood stage'])
    for i, sid in enumerate(ids):
        w.writerow([sid, f'{5 + i * 0.75:.2f}', 'export-only'])
with open('gage_height_iv.rdb', 'w') as f:
    f.write('# Instantaneous gage heights, feet\n')
    f.write('agency_cd\tsite_no\tdatetime\t00065\t00065_cd\n')
    f.write('5s\t15s\t16d\t10n\t4s\n')
    for i, sid in enumerate(ids):
        stage = 5 + i * 0.75
        for day, flag in enumerate(patterns[i], 1):
            if (i, day) in {(0, 4), (2, 6)}:
                continue
            for hour in (9, 17):
                height = stage + (0.65 if flag == '1' and hour == 17 else -0.65)
                height += random.uniform(-0.14, 0.14)
                f.write(f'USGS\t{sid}\t2025-06-{day:02d} {hour:02d}:00\t{height:.2f}\tA\n')
    f.write('USGS\t03310001\t2025-06-04 08:00\t\tA\n')
