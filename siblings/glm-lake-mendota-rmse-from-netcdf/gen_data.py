import os
import numpy as np
import pandas as pd
from scipy.io import netcdf_file

rng = np.random.default_rng(20240611)
LD = 21.0
FILL = np.float32(9.96921e36)
NT, L = 40, 30
START = pd.Timestamp("2009-01-01 12:00:00")


def frac():
    f = rng.uniform(0.05, 0.4)
    return f if rng.random() < 0.5 else 1.0 - f


def profile(depth, t):
    s = np.sin(np.pi * t / NT)
    te = 10.0 + 10.0 * s
    th = 6.0 + 2.0 * s
    zt = 5.0 + 4.0 * t / NT
    return th + (te - th) / (1.0 + np.exp((np.asarray(depth, dtype=float) - zt) / 1.5))


nml = """&glm_setup
   sim_name = 'LakeMendota'
   max_layers = 500
   min_layer_vol = 0.025
/
&morphometry
   lake_name = 'Mendota'
   latitude = 43.1
   bsn_vals = 5
   H = 375.0, 380.0, 385.0, 390.0, 396.0
   A = 0.0, 1.0e6, 1.5e7, 3.0e7, 3.9e7
/
&light
   Kw = 0.3
/
&mixing
   coef_mix_hyp = 0.5
/
&init_profiles
   lake_depth = 21.0
   num_depths = 3
   the_depths = 1, 10, 20
   the_temps = 4.0, 4.0, 4.0
/
&meteorology
   meteo_fl = 'bcs/meteo.csv'
   wind_factor = 1
/
"""
with open("glm3.nml", "w") as fh:
    fh.write(nml)

os.makedirs("output", exist_ok=True)
z = np.full((NT, L, 1, 1), FILL, dtype=np.float32)
temp = np.full((NT, L, 1, 1), FILL, dtype=np.float32)
for t in range(NT):
    nl = int(rng.integers(18, 29))
    ks = rng.integers(0, 21, size=nl)
    depths = np.array([k + frac() for k in ks])
    depths = np.sort(depths)[::-1]
    temps = profile(depths, t) + rng.normal(0, 0.05, nl)
    if rng.random() < 0.35:
        depths = np.append(depths, -rng.uniform(0.1, 0.4))
        temps = np.append(temps, float(profile(0.0, t)) + 2.5)
    n = len(depths)
    z[t, :n, 0, 0] = (LD - depths).astype(np.float32)
    temp[t, :n, 0, 0] = temps.astype(np.float32)

f = netcdf_file(os.path.join("output", "output.nc"), "w")
f.createDimension("time", NT)
f.createDimension("nlev", L)
f.createDimension("lat", 1)
f.createDimension("lon", 1)
tv = f.createVariable("time", "f8", ("time",))
tv[:] = 24.0 * np.arange(NT)
tv.units = "hours since 2009-01-01 12:00:00"
zv = f.createVariable("z", "f4", ("time", "nlev", "lat", "lon"))
zv[:] = z
zv.units = "meters"
zv.long_name = "layer heights above bottom"
zv._FillValue = FILL
tpv = f.createVariable("temp", "f4", ("time", "nlev", "lat", "lon"))
tpv[:] = temp
tpv.units = "celsius"
tpv._FillValue = FILL
f.close()

rows = []


def add(ts, tpos):
    nk = int(rng.integers(6, 12))
    kk = np.sort(rng.choice(21, size=nk, replace=False))
    for k in kk:
        d = max(0.0, k + rng.uniform(-0.3, 0.3))
        tt = float(profile(d, tpos)) + rng.normal(0, 0.9)
        rows.append((ts.strftime("%Y-%m-%d %H:%M:%S"), round(d, 2), round(tt, 2)))


for dd in np.sort(rng.choice(NT, size=22, replace=False)):
    add(START + pd.Timedelta(days=int(dd)), int(dd))
for dd in rng.choice(NT, size=5, replace=False):
    add(START + pd.Timedelta(days=int(dd), hours=-3), int(dd))
for dd in (44, 47, 52):
    add(START + pd.Timedelta(days=dd), NT - 1)

df = pd.DataFrame(rows, columns=["datetime", "depth", "temp"]).sort_values(["datetime", "depth"])
df.to_csv("field_temp_oxy.csv", index=False)
