import json
from pathlib import Path

import numpy as np
import pytest
from scipy import ndimage

WORK = Path("/root/work")
OUT = WORK / "dyn_masks.npz"


def expected():
    frames = np.load(WORK / "frames.npz")["frames"].astype(np.int32)
    T, H, W = frames.shape
    shifts = {int(d["frame"]): (int(d["dx"]), int(d["dy"]))
              for d in json.loads((WORK / "shifts.json").read_text())}
    masks = [np.zeros((H, W), bool)]
    for t in range(1, T):
        dx, dy = shifts[t]
        prev, curr = frames[t - 1], frames[t]
        warped = np.zeros_like(curr)
        valid = np.zeros((H, W), bool)
        y0, y1 = max(0, dy), min(H, H + dy)
        x0, x1 = max(0, dx), min(W, W + dx)
        warped[y0:y1, x0:x1] = prev[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
        valid[y0:y1, x0:x1] = True
        diff = np.abs(curr - warped)
        vals = diff[valid].astype(float)
        med = float(np.median(vals))
        mad = float(np.median(np.abs(vals - med)))
        thr = max(20.0, med + 3 * 1.4826 * mad)
        raw = valid & (diff > thr)
        lab, n = ndimage.label(raw, structure=np.ones((3, 3), dtype=int))
        mask = np.zeros((H, W), bool)
        for c in range(1, n + 1):
            comp = lab == c
            if comp.sum() >= 12:
                mask |= comp
        masks.append(mask)
    return (H, W), masks


@pytest.fixture
def npz():
    return np.load(OUT)


def decode(npz, i, H, W):
    indices = npz[f"f_{i}_indices"]
    indptr = npz[f"f_{i}_indptr"]
    m = np.zeros((H, W), bool)
    for r in range(H):
        m[r, indices[indptr[r]:indptr[r + 1]]] = True
    return m


def test_output_exists():
    assert OUT.exists(), "missing /root/work/dyn_masks.npz"


def test_shape_key(npz):
    (H, W), _ = expected()
    assert "shape" in npz.files
    assert [int(x) for x in npz["shape"]] == [H, W]


def test_frame_keys(npz):
    _, masks = expected()
    want = {f"f_{i}_{s}" for i in range(len(masks)) for s in ("data", "indices", "indptr")}
    got = {k for k in npz.files if k.startswith("f_")}
    assert got == want, f"missing {sorted(want - got)[:5]}, extra {sorted(got - want)[:5]}"


def test_csr_integrity(npz):
    (H, W), masks = expected()
    for i in range(len(masks)):
        data = npz[f"f_{i}_data"]
        ind = npz[f"f_{i}_indices"]
        ptr = npz[f"f_{i}_indptr"]
        assert ptr.shape[0] == H + 1, i
        assert int(ptr[0]) == 0, i
        assert np.all(np.diff(ptr) >= 0), i
        assert int(ptr[-1]) == ind.size == data.size, i
        assert ind.size == 0 or (ind.min() >= 0 and ind.max() < W), i
        assert np.all(data != 0), i


def test_masks_match(npz):
    (H, W), masks = expected()
    for i, exp in enumerate(masks):
        got = decode(npz, i, H, W)
        mism = int(np.sum(got != exp))
        assert mism <= 2, f"frame {i}: {mism} mismatched pixels (expected {int(exp.sum())} true)"
