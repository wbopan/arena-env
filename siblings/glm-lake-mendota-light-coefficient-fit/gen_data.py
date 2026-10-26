import random
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from scipy.io import netcdf_file

random.seed(317)
Path('bcs').mkdir(exist_ok=True)
Path('output').mkdir(exist_ok=True)
Path('glm3.nml').write_text("&init_profiles\n lake_depth = 25\n/\n&light\n Kw = 0.3000\n/\n&mixing\n coef_mix_hyp = 0.52\n/\n")
true_kw = random.uniform(0.16, 0.43)
heights = [2., 8., 14., 20., 24.]
shortwave = [random.randrange(110, 310) for _ in range(4)]
with netcdf_file('output/output.nc', 'w') as nc:
    nc.createDimension('time', 4)
    nc.createDimension('layer', 5)
    nc.createDimension('one', 1)
    nc.createVariable('time', 'f8', ('time',))[:] = np.arange(4) * 24.
    z = nc.createVariable('z', 'f8', ('time', 'layer', 'one', 'one'))
    t = nc.createVariable('temp', 'f8', ('time', 'layer', 'one', 'one'))
    for i in range(4):
        for j, h in enumerate(heights):
            z[i, j, 0, 0] = h
            t[i, j, 0, 0] = 8 + i * 0.7 + h * 0.31 + random.uniform(-0.2, 0.2)
met = ['datetime,shortwave_W_m2']
obs = ['datetime,depth_m,temp_C']
for i in range(4):
    date = (datetime(2009, 1, 1, 12) + timedelta(days=i)).isoformat()
    met.append(f'{date},{shortwave[i]}')
    for j, h in enumerate(heights):
        depth = 25 - h
        baseline = 8 + i * 0.7 + h * 0.31
        # Read back the stored simulated value, including its generated perturbation.
        with netcdf_file('output/output.nc', 'r', mmap=False) as nc:
            baseline = float(nc.variables['temp'][i, j, 0, 0])
        value = baseline + (true_kw - 0.3) * (depth - 10) * shortwave[i] / 200
        obs.append(f'{date},{depth:.1f},{value:.12f}')
Path('bcs/meteo.csv').write_text('\n'.join(met) + '\n')
Path('field_temp_oxy.csv').write_text('\n'.join(obs) + '\n')
