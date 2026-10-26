import random
from pathlib import Path
import numpy as np
from scipy.io import netcdf_file

random.seed(991)
Path('output').mkdir(exist_ok=True)
Path('bcs').mkdir(exist_ok=True)
Path('glm3.nml').write_text('&init_profiles\n lake_depth = 25\n/\n')
Path('bcs/hypsography.csv').write_text('height_m,area_m2\n0,2400000\n6,3600000\n13,5100000\n19,6800000\n25,9100000\n')
with netcdf_file('output/output.nc', 'w') as nc:
    nc.createDimension('time', 4)
    nc.createDimension('layer', 4)
    nc.createDimension('one', 1)
    nc.createVariable('time', 'f8', ('time',))[:] = np.array([0., 24., 48., 72.])
    z = nc.createVariable('z', 'f8', ('time', 'layer', 'one', 'one'))
    t = nc.createVariable('temp', 'f8', ('time', 'layer', 'one', 'one'))
    for i in range(4):
        heights = [2 + 0.15*i, 9 + 0.1*i, 16 - 0.1*i, 23 - 0.05*i]
        for j, height in enumerate(heights):
            z[i, j, 0, 0] = height
            t[i, j, 0, 0] = 5.5 + j*2.4 + i*0.65 + random.uniform(-0.35, 0.35)
