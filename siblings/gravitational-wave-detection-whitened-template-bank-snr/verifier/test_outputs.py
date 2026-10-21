import json
from pathlib import Path

import numpy as np
import pytest

W = Path("/root/work")
OUT = W / "results.json"
FS = 512.0


def expected():
    d = np.load(W / "data.npy").astype(np.float64)
    T = np.load(W / "templates.npy").astype(np.float64)
    res = []
    for h in T:
        M = len(h)
        n = len(d) - M + 1
        rho = np.array([np.dot(d[k:k + M], h) for k in range(n)]) / np.sqrt(np.sum(h * h))
        k = int(np.argmax(np.abs(rho)))
        res.append((float(abs(rho[k])), k / FS))
    return res


@pytest.fixture(scope="module")
def out():
    assert OUT.exists(), "results.json missing"
    return json.loads(OUT.read_text())


def test_file_exists():
    assert OUT.exists()


def test_schema(out):
    assert "templates" in out and "best_index" in out
    tl = out["templates"]
    assert isinstance(tl, list) and len(tl) == 6
    assert [int(e["index"]) for e in tl] == list(range(6))
    for e in tl:
        assert "peak_snr" in e and "peak_time_s" in e


def test_peak_snr(out):
    exp = expected()
    for e in out["templates"]:
        i = int(e["index"])
        assert abs(float(e["peak_snr"]) - exp[i][0]) < 2e-3, (i, e["peak_snr"], exp[i][0])


def test_peak_time(out):
    exp = expected()
    for e in out["templates"]:
        i = int(e["index"])
        assert abs(float(e["peak_time_s"]) - exp[i][1]) < 1e-3, (i, e["peak_time_s"], exp[i][1])


def test_best_index(out):
    exp = expected()
    best = int(np.argmax([s for s, _ in exp]))
    assert int(out["best_index"]) == best
