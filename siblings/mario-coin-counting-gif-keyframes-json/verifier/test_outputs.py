import json
import os

import numpy as np
from PIL import Image
from scipy import ndimage

WORK = "/root/work"
GIF = os.path.join(WORK, "level.gif")
OUT = os.path.join(WORK, "keyframes.json")


def expected():
    im = Image.open(GIF)
    n = im.n_frames
    lums, durs, rgbs = [], [], []
    for i in range(n):
        im.seek(i)
        rgb = np.array(im.convert("RGB"), dtype=np.int64)
        durs.append(int(im.info.get("duration", 0)))
        rgbs.append(rgb)
        a = rgb.astype(np.float64)
        lums.append(0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])
    keys = [0]
    for i in range(1, n):
        if np.abs(lums[i] - lums[keys[-1]]).mean() > 30:
            keys.append(i)
    out = []
    for k in keys:
        mask = np.all(rgbs[k] == np.array([252, 188, 60]), axis=-1)
        _, nc = ndimage.label(mask, structure=np.ones((3, 3), dtype=int))
        out.append({"index": k, "timestamp_ms": int(sum(durs[:k])), "coins": int(nc)})
    return n, out


def load():
    with open(OUT) as f:
        return json.load(f)


def test_output_exists_and_schema():
    assert os.path.isfile(OUT)
    d = load()
    assert isinstance(d, dict)
    assert "n_frames" in d and "keyframes" in d
    assert isinstance(d["keyframes"], list) and len(d["keyframes"]) > 0
    for k in d["keyframes"]:
        assert {"index", "timestamp_ms", "coins"} <= set(k.keys())


def test_n_frames():
    n, _ = expected()
    assert int(load()["n_frames"]) == n


def test_keyframe_indices():
    _, exp = expected()
    got = [int(k["index"]) for k in load()["keyframes"]]
    assert got == [e["index"] for e in exp]


def test_timestamps():
    _, exp = expected()
    got = [int(round(float(k["timestamp_ms"]))) for k in load()["keyframes"]]
    assert got == [e["timestamp_ms"] for e in exp]


def test_coin_counts():
    _, exp = expected()
    got = [int(k["coins"]) for k in load()["keyframes"]]
    assert got == [e["coins"] for e in exp]
