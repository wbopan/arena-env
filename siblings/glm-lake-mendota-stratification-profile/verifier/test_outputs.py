import os
import re

import numpy as np
import pandas as pd
from scipy.io import netcdf_file

WORK = "/root/work"
OUT = os.path.join(WORK, "stratification.csv")
COLS = ["datetime", "surface_temp", "bottom_temp", "density_diff", "stratified", "thermocline_depth"]


def rho(T):
    return 1000.0 * (1.0 - (T + 288.9414) / (508929.2 * (T + 68.12963)) * (T - 3.9863) ** 2)


def expected():
    txt = open(os.path.join(WORK, "glm3.nml")).read()
    sec = re.search(r"&init_profiles(.*?)\n\s*/", txt, re.S).group(1)
    ld = float(re.search(r"lake_depth\s*=\s*([-+0-9.eE]+)", sec).group(1))
    tsec = re.search(r"&time(.*?)\n\s*/", txt, re.S).group(1)
    start = pd.Timestamp(re.search(r"start\s*=\s*'([^']+)'", tsec).group(1))
    f = netcdf_file(os.path.join(WORK, "output", "output.nc"), "r", mmap=False)
    time = np.array(f.variables["time"][:], dtype=float)
    ns = np.array(f.variables["NS"][:]).astype(int)
    z = np.array(f.variables["z"][:], dtype=float)
    tp = np.array(f.variables["temp"][:], dtype=float)
    f.close()
    rows = []
    for i in range(len(time)):
        n = ns[i]
        d = ld - z[i, :n, 0, 0]
        T = tp[i, :n, 0, 0]
        o = np.argsort(d)
        d, T = d[o], T[o]
        dr = rho(T[-1]) - rho(T[0])
        st = int(dr > 0.1)
        th = np.nan
        if st:
            g = np.abs(np.diff(T)) / np.diff(d)
            k = int(np.argmax(g))
            th = 0.5 * (d[k] + d[k + 1])
        dt = (start + pd.Timedelta(hours=float(time[i]))).strftime("%Y-%m-%d %H:%M")
        rows.append((dt, T[0], T[-1], dr, st, th))
    return pd.DataFrame(rows, columns=COLS)


def load():
    return pd.read_csv(OUT, dtype={"datetime": str})


def test_output_exists():
    assert os.path.exists(OUT), "stratification.csv not found"


def test_columns_and_rows():
    df = load()
    assert list(df.columns) == COLS, f"columns {list(df.columns)}"
    exp = expected()
    assert len(df) == len(exp)
    assert [s.strip() for s in df["datetime"]] == list(exp["datetime"])


def test_surface_bottom_temps():
    df, exp = load(), expected()
    assert np.allclose(df["surface_temp"].astype(float), exp["surface_temp"], atol=2e-3)
    assert np.allclose(df["bottom_temp"].astype(float), exp["bottom_temp"], atol=2e-3)


def test_density_and_flag():
    df, exp = load(), expected()
    assert np.allclose(df["density_diff"].astype(float), exp["density_diff"], atol=3e-4)
    assert list(df["stratified"].astype(int)) == list(exp["stratified"])


def test_thermocline_depth():
    df, exp = load(), expected()
    got = pd.to_numeric(df["thermocline_depth"], errors="coerce").to_numpy()
    want = exp["thermocline_depth"].to_numpy()
    for g, w, s in zip(got, want, exp["stratified"]):
        if s:
            assert np.isfinite(g) and abs(g - w) <= 0.011, f"thermocline {g} vs {w}"
        else:
            assert np.isnan(g), "thermocline_depth must be empty when not stratified"
