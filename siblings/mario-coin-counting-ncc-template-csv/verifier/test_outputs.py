import csv
import glob
import os

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from PIL import Image

WORK = "/root/work"
OUT = os.path.join(WORK, "counts.csv")


def luma(path):
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def count(img, tpl, thr=0.9, rad=3):
    win = sliding_window_view(img, tpl.shape)
    tz = tpl - tpl.mean()
    tn = np.sqrt((tz * tz).sum())
    wz = win - win.mean(axis=(2, 3), keepdims=True)
    wn = np.sqrt((wz * wz).sum(axis=(2, 3)))
    num = (wz * tz).sum(axis=(2, 3))
    den = wn * tn
    score = np.zeros_like(num)
    ok = den > 1e-9
    score[ok] = num[ok] / den[ok]
    ys, xs = np.nonzero(score >= thr)
    cand = sorted(zip(score[ys, xs], ys, xs), key=lambda t: -t[0])
    kept = []
    for s, y, x in cand:
        if all(max(abs(int(y) - ky), abs(int(x) - kx)) > rad for ky, kx in kept):
            kept.append((int(y), int(x)))
    return len(kept)


def expected():
    coin = luma(os.path.join(WORK, "coin.png"))
    goomba = luma(os.path.join(WORK, "goomba.png"))
    rows = []
    for p in sorted(glob.glob(os.path.join(WORK, "frames", "frame_*.png"))):
        img = luma(p)
        rows.append((os.path.basename(p), count(img, coin), count(img, goomba)))
    return rows


def read_out():
    with open(OUT, newline="") as f:
        return [r for r in csv.reader(f) if r]


def test_output_exists():
    assert os.path.isfile(OUT)


def test_header():
    rows = read_out()
    assert [c.strip() for c in rows[0]] == ["frame_id", "coins", "goombas"]


def test_frame_ids():
    rows = read_out()[1:]
    assert [r[0].strip() for r in rows] == [e[0] for e in expected()]


def test_coin_counts():
    rows = read_out()[1:]
    exp = expected()
    assert len(rows) == len(exp)
    assert [int(float(r[1])) for r in rows] == [e[1] for e in exp]


def test_goomba_counts():
    rows = read_out()[1:]
    exp = expected()
    assert len(rows) == len(exp)
    assert [int(float(r[2])) for r in rows] == [e[2] for e in exp]
