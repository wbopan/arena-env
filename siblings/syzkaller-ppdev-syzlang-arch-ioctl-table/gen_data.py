import csv
import random

random.seed(80419)
names = ['PPCLAIM', 'PPRELEASE', 'PPGETMODE', 'PPSETMODE', 'PPFROBCTRL', 'PPGETFLAGS', 'PPSETFLAGS', 'PPNEGOT']
directions = ['IO', 'IO', 'IOR', 'IOW', 'IOWR', 'IOR', 'IOW', 'IOWR']
rows = []
for name, direction in zip(names, directions):
    nr = random.randrange(0x10, 0xe0)
    size386 = 0 if direction == 'IO' else random.choice([1, 2, 4, 8, 12])
    size64 = size386 if direction == 'IO' else size386 + random.choice([0, 0, 4, 8])
    rows.append([name, '0x70', hex(nr), direction, size386, size64])
random.shuffle(rows)
with open('ioctl_layout.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['name', 'type', 'nr', 'direction', 'size_386', 'size_amd64'])
    w.writerows(rows)
