import csv
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

W = Path("/root/work")
OUT = W / "rar.csv"
COLS = ["country", "gold_value_musd", "exposure_musd", "total_reserves_musd", "rar_pct"]


def sheet_2025(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    d = {}
    for _, r in df.iterrows():
        v = r["2025"]
        if pd.notna(v):
            d[str(r["Country"]).strip()] = float(v)
    return d


def expected():
    g = pd.read_csv(W / "gold_monthly.csv")
    pr = g["price_usd_per_ozt"].to_numpy(float)
    r = 100 * np.diff(np.log(pr))
    sigma = float(np.std(r[-3:], ddof=1))
    avg = float(g[g["period"].astype(str).str.startswith("2025")]["price_usd_per_ozt"].mean())
    x = pd.read_excel(W / "reserves.xlsx", sheet_name=None)
    val = sheet_2025(x["Value"])
    vol = sheet_2025(x["Volume"])
    tot = sheet_2025(x["Total Reserves"])
    gv = dict(val)
    for c, v in vol.items():
        if c not in gv:
            gv[c] = v * avg
    res = {}
    for c, v in gv.items():
        if c in tot:
            e = v * sigma / 100
            res[c] = (v, e, tot[c], e / tot[c] * 100)
    return res


def read_out():
    with open(OUT, newline="") as f:
        rows = list(csv.reader(f))
    return [h.strip() for h in rows[0]], [r for r in rows[1:] if any(x.strip() for x in r)]


def close(a, b, tol):
    return abs(a - b) <= tol + 1e-7 * abs(b)


def test_exists():
    assert OUT.exists()


def test_header():
    hdr, _ = read_out()
    assert hdr == COLS


def test_country_set():
    _, rows = read_out()
    got = [r[0].strip() for r in rows]
    assert len(got) == len(set(got))
    assert set(got) == set(expected().keys())


def test_values():
    exp = expected()
    _, rows = read_out()
    for r in rows:
        c = r[0].strip()
        v, e, t, rar = exp[c]
        assert close(float(r[1]), v, 0.01), (c, r[1], v)
        assert close(float(r[2]), e, 0.01), (c, r[2], e)
        assert close(float(r[3]), t, 0.01), (c, r[3], t)
        assert close(float(r[4]), rar, 0.001), (c, r[4], rar)


def test_sorted_desc():
    _, rows = read_out()
    vals = [float(r[4]) for r in rows]
    assert vals == sorted(vals, reverse=True)
