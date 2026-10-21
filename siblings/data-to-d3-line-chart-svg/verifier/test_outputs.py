import csv
import datetime
import glob
import os
import re
import xml.etree.ElementTree as ET

import pytest

W = "/root/work"
OUT = os.path.join(W, "chart.svg")
NUM = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def expected():
    data = {}
    for f in sorted(glob.glob(os.path.join(W, "data", "indiv-stock", "*.csv"))):
        t = os.path.splitext(os.path.basename(f))[0]
        with open(f, newline="") as fh:
            rows = [(datetime.date.fromisoformat(r["Date"]), float(r["Close"])) for r in csv.DictReader(fh)]
        rows.sort()
        data[t] = rows
    dates = [d for v in data.values() for d, _ in v]
    closes = [c for v in data.values() for _, c in v]
    d0, d1 = min(dates), max(dates)
    c0, c1 = min(closes), max(closes)
    span = (d1 - d0).days
    exp = {}
    for t, rows in data.items():
        exp[t] = [(50 + 530 * (d - d0).days / span, 270 - 250 * (c - c0) / (c1 - c0)) for d, c in rows]
    return exp


def local(tag):
    return tag.split("}")[-1] if isinstance(tag, str) else ""


@pytest.fixture(scope="module")
def root():
    assert os.path.exists(OUT), "chart.svg missing"
    return ET.parse(OUT).getroot()


def elems(root, tag, cls):
    out = {}
    for el in root.iter():
        if local(el.tag) == tag and cls in (el.get("class") or "").split():
            out[el.get("data-ticker")] = el
    return out


def points(d):
    assert d.strip().startswith("M"), "path must start with M"
    nums = [float(x) for x in NUM.findall(d)]
    assert len(nums) % 2 == 0
    return list(zip(nums[0::2], nums[1::2]))


def test_svg_root(root):
    assert local(root.tag) == "svg"
    assert float(root.get("width")) == 600 and float(root.get("height")) == 300


def test_one_path_per_ticker(root):
    paths = elems(root, "path", "line")
    assert set(paths) == set(expected())


def test_point_counts(root):
    paths = elems(root, "path", "line")
    for t, pts in expected().items():
        assert len(points(paths[t].get("d"))) == len(pts), t


def test_path_coordinates(root):
    paths = elems(root, "path", "line")
    for t, pts in expected().items():
        got = points(paths[t].get("d"))
        for (gx, gy), (ex, ey) in zip(got, pts):
            assert abs(gx - ex) <= 0.011 and abs(gy - ey) <= 0.011, (t, gx, gy, ex, ey)


def test_labels(root):
    labels = elems(root, "text", "label")
    for t, pts in expected().items():
        assert t in labels, f"label for {t} missing"
        el = labels[t]
        assert (el.text or "").strip() == t
        ex, ey = pts[-1]
        assert abs(float(el.get("x")) - (ex + 5)) <= 0.011, t
        assert abs(float(el.get("y")) - ey) <= 0.011, t
