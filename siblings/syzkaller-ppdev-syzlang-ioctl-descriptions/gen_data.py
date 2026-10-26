import csv
import random

random.seed(61142)
rows = [
    ('PPCLAIM', 'none', 'none'),
    ('PPRELEASE', 'none', 'none'),
    ('PPGETMODE', 'int32', 'out'),
    ('PPSETMODE', 'int32', 'in'),
    ('PPFROBCTRL', 'frob', 'in'),
    ('PPGETSTATUS', 'int8', 'out'),
    ('PPGETFLAGS', 'int32', 'out'),
    ('PPSETFLAGS', 'int32', 'in'),
    ('PPDATADIR', 'int32', 'inout'),
]
random.shuffle(rows)
with open('ppdev_commands.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['name', 'argument', 'direction'])
    w.writerows(rows)
