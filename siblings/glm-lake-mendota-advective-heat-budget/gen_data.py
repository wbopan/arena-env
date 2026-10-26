import random
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from scipy.io import netcdf_file

random.seed(802)
Path('bcs').mkdir(exist_ok=True)
Path('output').mkdir(exist_ok=True)
Path('glm3.nml').write_text("&inflow\n inflow_fl = 'bcs/yahara.csv','bcs/tributary.csv'\n/\n&outflow\n outflow_fl = 'bcs/outflow.csv'\n/\n")
dates = [(datetime(2009, 1, 1) + timedelta(days=i)).date().isoformat() for i in range(5)]
for filename, base in [('yahara.csv', 12), ('tributary.csv', 4)]:
    lines = ['date,flow_m3_s,temp_C']
    for date in dates:
        lines.append(f'{date},{base + random.uniform(-2, 3):.4f},{9 + random.uniform(-2, 6):.4f}')
    Path('bcs', filename).write_text('\n'.join(lines) + '\n')
lines = ['date,flow_m3_s']
for date in dates:
    lines.append(f'{date},{random.uniform(12, 20):.4f}')
Path('bcs/outflow.csv').write_text('\n'.join(lines) + '\n')
with netcdf_file('output/output.nc', 'w') as nc:
    nc.createDimension('time', 5)
    nc.createDimension('layer', 3)
    nc.createDimension('one', 1)
    nc.createVariable('time', 'f8', ('time',))[:] = np.arange(5) * 24.
    z = nc.createVariable('z', 'f8', ('time', 'layer', 'one', 'one'))
    t = nc.createVariable('temp', 'f8', ('time', 'layer', 'one', 'one'))
    for i in range(5):
        for j, h in enumerate([4., 14., 24.]):
            z[i, j, 0, 0] = h
            t[i, j, 0, 0] = 6 + j * 2 + i * 0.5 + random.uniform(-0.3, 0.3)
