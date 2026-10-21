import csv
import glob
import os
from pathlib import Path

import numpy as np
import pytest

WORK = Path("/root/work")
OUT = WORK / "triggers.csv"


def _expected():
    res = {}
    for f in sorted(glob.glob(str(WORK / "trace_*.npz"))):
        d = np.load(f)
        dt = float(d["dt"])
        names = [c.strip() for c in str(d["channels"]).split(",")]
        zi = [k for k, c in enumerate(names) if c.endswith("Z")][0]
        x = np.asarray(d["data"][:, zi], dtype=np.float64)
        x = x - x.mean()
        e = x * x
        ns = int(round(0.5 / dt))
        nl = int(round(5.0 / dt))
        cs = np.concatenate([[0.0], np.cumsum(e)])
        idx = np.arange(nl - 1, len(e))
        sta = (cs[idx + 1] - cs[idx + 1 - ns]) / ns
        lta = (cs[idx + 1] - cs[idx + 1 - nl]) / nl
        hit = np.nonzero(sta >= 3.0 * lta)[0]
        trig = int(idx[hit[0]]) if len(hit) else -1
        res[os.path.basename(f)] = (trig, dt)
    return res


@pytest.fixture(scope="module")
def expected():
    return _expected()


@pytest.fixture(scope="module")
def rows():
    assert OUT.exists(), "triggers.csv missing"
    with open(OUT, newline="") as fh:
        reader = csv.DictReader(fh)
        header = [h.strip() for h in reader.fieldnames]
        data = [{k.strip(): v.strip() for k, v in r.items()} for r in reader]
    return header, data


def test_file_exists():
    assert OUT.exists()


def test_header_and_rows(rows, expected):
    header, data = rows
    assert header == ["file_name", "trigger_idx", "trigger_time_s"]
    names = [r["file_name"] for r in data]
    assert sorted(names) == sorted(expected.keys())
    assert len(names) == len(set(names))


def test_no_trigger_cases(rows, expected):
    _, data = rows
    for r in data:
        exp, _ = expected[r["file_name"]]
        idx = int(float(r["trigger_idx"]))
        if exp == -1:
            assert idx == -1, r
            assert float(r["trigger_time_s"]) == -1, r
        else:
            assert idx != -1, r


def test_trigger_indices(rows, expected):
    _, data = rows
    for r in data:
        exp, _ = expected[r["file_name"]]
        if exp == -1:
            continue
        idx = int(float(r["trigger_idx"]))
        assert abs(idx - exp) <= 2, (r, exp)


def test_trigger_times(rows, expected):
    _, data = rows
    for r in data:
        exp, dt = expected[r["file_name"]]
        if exp == -1:
            continue
        idx = int(float(r["trigger_idx"]))
        t = float(r["trigger_time_s"])
        assert abs(t - idx * dt) <= 0.0015, r
        assert abs(t - exp * dt) <= 2 * dt + 0.001, (r, exp * dt)
