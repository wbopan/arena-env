import json
import math
from pathlib import Path

import numpy as np
import pytest

WORK = Path("/root/work")
OUT = WORK / "pred_instructions.json"
VALID = {"Stay", "Dolly In", "Dolly Out", "Pan Left", "Pan Right",
         "Tilt Up", "Tilt Down", "Roll Left", "Roll Right"}


def expected_labels():
    n = json.loads((WORK / "meta.json").read_text())["num_frames"]
    rows = np.loadtxt(WORK / "tracks.csv", delimiter=",", skiprows=1)
    out = []
    for i in range(n - 1):
        r = rows[rows[:, 0].astype(int) == i]
        x0, y0, x1, y1 = r[:, 1], r[:, 2], r[:, 3], r[:, 4]
        one = np.ones_like(x0)
        zero = np.zeros_like(x0)
        A = np.vstack([np.column_stack([x0, -y0, one, zero]),
                       np.column_stack([y0, x0, zero, one])])
        rhs = np.concatenate([x1, y1])
        a, b, tx, ty = np.linalg.lstsq(A, rhs, rcond=None)[0]
        s = math.hypot(a, b)
        rot = math.atan2(b, a)
        lab = set()
        if abs(s - 1) > 0.02:
            lab.add("Dolly In" if s > 1 else "Dolly Out")
        if abs(rot) > 0.01:
            lab.add("Roll Right" if rot > 0 else "Roll Left")
        if abs(tx) > 2 and abs(tx) >= abs(ty):
            lab.add("Pan Left" if tx > 0 else "Pan Right")
        if abs(ty) > 2 and abs(ty) > abs(tx):
            lab.add("Tilt Up" if ty > 0 else "Tilt Down")
        out.append(lab or {"Stay"})
    out.append(out[-1])
    return out


def intervals(pred):
    iv = []
    for k, v in pred.items():
        s, e = k.split("->")
        iv.append((int(s), int(e), frozenset(v)))
    return sorted(iv, key=lambda t: (t[0], t[1]))


@pytest.fixture
def pred():
    return json.loads(OUT.read_text())


def test_output_exists():
    assert OUT.exists(), "missing /root/work/pred_instructions.json"


def test_schema(pred):
    assert isinstance(pred, dict) and len(pred) > 0
    for k, v in pred.items():
        parts = k.split("->")
        assert len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit(), k
        assert int(parts[1]) > int(parts[0]), k
        assert isinstance(v, list) and len(v) > 0, k
        assert all(isinstance(x, str) and x in VALID for x in v), v
        assert len(set(v)) == len(v), v


def test_coverage(pred):
    n = len(expected_labels())
    pos = 0
    for s, e, _ in intervals(pred):
        assert s == pos, f"gap or overlap at frame {s}"
        pos = e
    assert pos == n, f"coverage ends at {pos}, expected {n}"


def test_intervals_merged(pred):
    iv = intervals(pred)
    for a, b in zip(iv, iv[1:]):
        assert a[2] != b[2], f"adjacent intervals {a[:2]} and {b[:2]} share labels"


def test_labels_match(pred):
    exp = expected_labels()
    got = {}
    for s, e, lab in intervals(pred):
        for f in range(s, e):
            got[f] = set(lab)
    bad = [(f, sorted(got.get(f, [])), sorted(exp[f])) for f in range(len(exp)) if got.get(f) != exp[f]]
    assert not bad, f"label mismatches: {bad[:5]}"
