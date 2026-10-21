import csv
import json
import os
import re

import numpy as np
import openpyxl
import pytest

W = "/root/work"
OUT = os.path.join(W, "cycle_stats.json")
YEARS = list(range(1980, 2025))


def read_table(path):
    ws = openpyxl.load_workbook(path, data_only=True)["Table"]
    ann, qs = {}, {}
    for row in ws.iter_rows(min_row=1, values_only=True):
        if not row or row[0] is None or len(row) < 2 or row[1] is None:
            continue
        k, v = row[0], row[1]
        if not isinstance(v, (int, float)):
            continue
        if isinstance(k, (int, float)):
            ann[int(k)] = float(v)
        elif isinstance(k, str):
            s = k.strip()
            if re.fullmatch(r"\d{4}", s):
                ann[int(s)] = float(v)
                continue
            m = re.fullmatch(r"(\d{4})\s*:\s*(I|II|III|IV)", s)
            if m:
                qs.setdefault(int(m.group(1)), []).append(float(v))
    return np.array([ann[y] if y in ann else np.mean(qs[y]) for y in YEARS])


def hp_cycle(y, lam):
    T = len(y)
    D = np.zeros((T - 2, T))
    for i in range(T - 2):
        D[i, i], D[i, i + 1], D[i, i + 2] = 1.0, -2.0, 1.0
    return y - np.linalg.solve(np.eye(T) + lam * D.T @ D, y)


@pytest.fixture(scope="module")
def expected():
    cp = {}
    with open(os.path.join(W, "cpi_monthly.csv")) as f:
        for r in csv.DictReader(f):
            cp.setdefault(int(r["observation_date"][:4]), []).append(float(r["CPIAUCSL"]))
    cpi = np.array([np.mean(cp[y]) for y in YEARS])
    cc = hp_cycle(np.log(read_table(os.path.join(W, "pce_nominal.xlsx")) / cpi * 100), 100)
    ci = hp_cycle(np.log(read_table(os.path.join(W, "pfi_nominal.xlsx")) / cpi * 100), 100)
    sc = np.std(cc, ddof=1) * 100
    si = np.std(ci, ddof=1) * 100
    return {"n_years": len(YEARS), "std_pce_pct": sc, "std_pfi_pct": si,
            "relative_volatility": si / sc, "corr": float(np.corrcoef(cc, ci)[0, 1])}


@pytest.fixture(scope="module")
def out():
    assert os.path.exists(OUT), "cycle_stats.json missing"
    with open(OUT) as f:
        return json.load(f)


def test_file_exists():
    assert os.path.exists(OUT)


def test_schema(out):
    for k in ["n_years", "std_pce_pct", "std_pfi_pct", "relative_volatility", "corr"]:
        assert k in out, k
    assert int(out["n_years"]) == 45


def test_std_values(out, expected):
    assert abs(float(out["std_pce_pct"]) - expected["std_pce_pct"]) < 2e-3
    assert abs(float(out["std_pfi_pct"]) - expected["std_pfi_pct"]) < 2e-3


def test_relative_volatility(out, expected):
    assert abs(float(out["relative_volatility"]) - expected["relative_volatility"]) < 2e-3


def test_corr(out, expected):
    assert abs(float(out["corr"]) - expected["corr"]) < 2e-3
