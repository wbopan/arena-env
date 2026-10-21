import json
import os
import re

import numpy as np
import pandas as pd
from scipy.io import netcdf_file

WORK = "/root/work"
OUT = os.path.join(WORK, "rmse.json")
TOL = 1e-3


def lake_depth():
    txt = open(os.path.join(WORK, "glm3.nml")).read()
    sec = re.search(r"&init_profiles(.*?)\n\s*/", txt, re.S).group(1)
    return float(re.search(r"lake_depth\s*=\s*([-+0-9.eE]+)", sec).group(1))


def expected():
    ld = lake_depth()
    f = netcdf_file(os.path.join(WORK, "output", "output.nc"), "r", mmap=False)
    time = np.array(f.variables["time"][:], dtype=float)
    z = np.array(f.variables["z"][:], dtype=float)
    tp = np.array(f.variables["temp"][:], dtype=float)
    f.close()
    start = pd.Timestamp("2009-01-01 12:00:00")
    rec = []
    for i in range(len(time)):
        dt = start + pd.Timedelta(hours=float(time[i]))
        for j in range(z.shape[1]):
            zz = z[i, j, 0, 0]
            tt = tp[i, j, 0, 0]
            if not (np.isfinite(zz) and np.isfinite(tt)) or abs(zz) > 1e30 or abs(tt) > 1e30:
                continue
            d = ld - zz
            if 0 <= d <= ld:
                rec.append({"datetime": dt, "depth": int(round(d)), "temp_sim": tt})
    sim = pd.DataFrame(rec).groupby(["datetime", "depth"], as_index=False)["temp_sim"].mean()
    obs = pd.read_csv(os.path.join(WORK, "field_temp_oxy.csv"))
    obs["datetime"] = pd.to_datetime(obs["datetime"])
    obs["depth"] = obs["depth"].round().astype(int)
    m = pd.merge(obs, sim, on=["datetime", "depth"], how="inner")
    diff = (m["temp_sim"] - m["temp"]).to_numpy()
    return float(np.sqrt(np.mean(diff ** 2))), float(np.mean(diff)), int(len(m))


def load():
    with open(OUT) as fh:
        return json.load(fh)


def test_output_exists():
    assert os.path.exists(OUT), "rmse.json not found"


def test_schema():
    d = load()
    for k in ("rmse", "bias", "n_matched"):
        assert k in d, f"missing key {k}"
    assert isinstance(d["n_matched"], int)
    float(d["rmse"])
    float(d["bias"])


def test_n_matched():
    _, _, n = expected()
    assert load()["n_matched"] == n, f"expected {n} matched pairs"


def test_rmse():
    r, _, _ = expected()
    assert abs(float(load()["rmse"]) - r) <= TOL, f"expected rmse {r:.4f}"


def test_bias():
    _, b, _ = expected()
    assert abs(float(load()["bias"]) - b) <= TOL, f"expected bias {b:.4f}"
