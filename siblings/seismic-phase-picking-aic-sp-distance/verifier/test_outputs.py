import glob
import json
from pathlib import Path

import numpy as np
import pytest

WORK = Path("/root/work")
OUT = WORK / "picks.json"
FACTOR = 6.0 * 3.5 / (6.0 - 3.5)


def _aic(y):
    y = np.asarray(y, dtype=np.float64)
    y = y - y.mean()
    M = len(y)
    c1 = np.cumsum(y)
    c2 = np.cumsum(y * y)
    k = np.arange(10, M - 10)
    sl = c1[k - 1]
    ql = c2[k - 1]
    vl = ql / k - (sl / k) ** 2
    nr = M - k
    sr = c1[-1] - sl
    qr = c2[-1] - ql
    vr = qr / nr - (sr / nr) ** 2
    a = k * np.log(vl) + (M - k - 1) * np.log(vr)
    return int(k[np.argmin(a)])


@pytest.fixture(scope="module")
def expected():
    res = {}
    for f in sorted(glob.glob(str(WORK / "sta_*.npz"))):
        d = np.load(f)
        dt = float(d["dt"])
        code = str(d["station"])
        names = [c.strip() for c in str(d["channels"]).split(",")]
        zi = [i for i, c in enumerate(names) if c.endswith("Z")][0]
        ni = [i for i, c in enumerate(names) if c.endswith("N")][0]
        data = np.asarray(d["data"], dtype=np.float64)
        p = _aic(data[:, zi])
        w = p + int(round(0.2 / dt))
        s = w + _aic(data[w:, ni])
        sp = (s - p) * dt
        res[code] = {"p": p, "s": s, "sp": sp, "dist": sp * FACTOR, "dt": dt}
    return res


@pytest.fixture(scope="module")
def out():
    assert OUT.exists(), "picks.json missing"
    with open(OUT) as fh:
        return json.load(fh)


def test_schema(out, expected):
    assert "stations" in out and "nearest_station" in out
    assert set(out["stations"].keys()) == set(expected.keys())
    for code, rec in out["stations"].items():
        for key in ("p_idx", "s_idx", "sp_time_s", "distance_km"):
            assert key in rec, (code, key)


def test_p_picks(out, expected):
    for code, e in expected.items():
        assert abs(int(out["stations"][code]["p_idx"]) - e["p"]) <= 2, (code, e["p"])


def test_s_picks(out, expected):
    for code, e in expected.items():
        assert abs(int(out["stations"][code]["s_idx"]) - e["s"]) <= 2, (code, e["s"])


def test_sp_and_distance(out, expected):
    for code, e in expected.items():
        rec = out["stations"][code]
        dt = e["dt"]
        sp = float(rec["sp_time_s"])
        dist = float(rec["distance_km"])
        own = (int(rec["s_idx"]) - int(rec["p_idx"])) * dt
        assert abs(sp - own) <= 0.002, (code, sp, own)
        assert abs(sp - e["sp"]) <= 4 * dt + 0.002, (code, sp, e["sp"])
        assert abs(dist - sp * FACTOR) <= 0.02, (code, dist)
        assert abs(dist - e["dist"]) <= FACTOR * 4 * dt + 0.02, (code, dist, e["dist"])


def test_nearest_station(out, expected):
    best = min(expected, key=lambda c: expected[c]["dist"])
    assert out["nearest_station"] == best
