import csv
import random

random.seed(39071)
names = ['PPCLAIM', 'PPRELEASE', 'PPGETMODE', 'PPSETMODE', 'PPFROBCTRL', 'PPGETFLAGS', 'PPSETFLAGS', 'PPNEGOT']
directions = ['in', 'in', 'out', 'in', 'inout', 'out', 'in', 'inout']
items = list(zip(names, directions))
random.shuffle(items)
with open('uapi_commands.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['name', 'direction'])
    w.writerows(items)
wrong = {items[1][0], items[5][0]}
other = {'in': 'out', 'out': 'inout', 'inout': 'in'}
lines = ['include <linux/ppdev.h>', 'resource fd_ppdev[fd]']
for name, direction in items:
    actual = other[direction] if name in wrong else direction
    lines.append(f'ioctl${name}(fd fd_ppdev, cmd const[{name}], arg ptr[{actual}, int32])')
with open('dev_audit.txt', 'w') as f:
    f.write('\n'.join(lines) + '\n')
missing = {items[2][0], items[6][0]}
constants = ['arches = 386, amd64']
for i, (name, _) in enumerate(items):
    if name not in missing:
        constants.append(f'{name} = {0x7000 + i * 7 + random.randrange(7)}')
constants.append('PPUNUSED = 28800')
with open('dev_audit.txt.const', 'w') as f:
    f.write('\n'.join(constants) + '\n')
