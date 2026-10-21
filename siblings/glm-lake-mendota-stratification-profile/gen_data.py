import os
import numpy as np
from scipy.io import netcdf_file

rng = np.random.default_rng(31337)
LD = 18.0
NT, L = 30, 28

nml = """&glm_setup
   sim_name = 'LakeMendota'
   max_layers = 500
/
&time
   timefmt = 2
   start = '2010-05-01 00:00:00'
   stop = '2010-05-16 00:00:00'
   dt = 3600.0
/
&light
   Kw = 0.3
/
&init_profiles
   lake_depth = 18.0
   num_depths = 2
   the_depths = 1, 17
   the_temps = 8.0, 8.0
/
&output
   out_dir = 'output'
   out_fn = 'output'
   nsave = 12
/
"""
with open("glm3.nml", "w") as fh:
    fh.write(nml)

ns = np.zeros(NT, dtype=np.int32)
z = np.zeros((NT, L, 1, 1), dtype=np.float32)
temp = np.zeros((NT, L, 1, 1), dtype=np.float32)
for t in range(NT):
    nl = int(rng.integers(15, 26))
    depths = np.sort(rng.uniform(0.1, 17.9, nl))[::-1]
    if 8 <= t < 24:
        te = rng.uniform(18, 24)
        th = rng.uniform(9, 12)
        zt = rng.uniform(4, 9)
        T = th + (te - th) / (1.0 + np.exp((depths - zt) / 0.8)) + rng.normal(0, 0.02, nl)
    else:
        base = rng.uniform(8, 12)
        T = base + rng.uniform(-0.08, 0.08, nl)
    z[t, :nl, 0, 0] = (LD - depths).astype(np.float32)
    temp[t, :nl, 0, 0] = T.astype(np.float32)
    z[t, nl:, 0, 0] = rng.uniform(0, LD, L - nl).astype(np.float32)
    temp[t, nl:, 0, 0] = rng.uniform(0, 30, L - nl).astype(np.float32)
    ns[t] = nl

os.makedirs("output", exist_ok=True)
f = netcdf_file(os.path.join("output", "output.nc"), "w")
f.createDimension("time", NT)
f.createDimension("nlev", L)
f.createDimension("lat", 1)
f.createDimension("lon", 1)
tv = f.createVariable("time", "f8", ("time",))
tv[:] = 12.0 * np.arange(NT)
tv.units = "hours since 2010-05-01 00:00:00"
nv = f.createVariable("NS", "i", ("time",))
nv[:] = ns
nv.long_name = "number of layers"
zv = f.createVariable("z", "f4", ("time", "nlev", "lat", "lon"))
zv[:] = z
zv.units = "meters"
tpv = f.createVariable("temp", "f4", ("time", "nlev", "lat", "lon"))
tpv[:] = temp
tpv.units = "celsius"
f.close()
