import json
from pathlib import Path

import openpyxl
import pytest

W = Path("/root/work")
OUT = W / "import_content.json"
KEYS = {"import_content_share", "gfcf_total", "top_import_contributor", "import_ratios"}


def _rows(ws):
    d = {}
    for r in ws.iter_rows(min_row=4, values_only=True):
        if r[0] is None:
            continue
        c = str(r[0]).strip()
        if c.upper() == "TOTAL":
            continue
        d[c] = r
    return d


def expected():
    wb = openpyxl.load_workbook(W / "sut.xlsx", data_only=True)
    s = _rows(wb["SUPPLY"])
    u = _rows(wb["USE"])
    ratios = {c: float(s[c][3]) / float(s[c][6]) for c in s}
    gf = {c: float(u[c][5] or 0) for c in u}
    tot = sum(gf.values())
    share = sum(gf[c] * ratios[c] for c in gf) / tot
    top = max(gf, key=lambda c: gf[c] * ratios[c])
    return ratios, tot, share, top


@pytest.fixture(scope="module")
def out():
    assert OUT.exists(), "output file missing"
    return json.loads(OUT.read_text())


def test_schema(out):
    assert isinstance(out, dict)
    assert set(out.keys()) == KEYS


def test_share(out):
    _, _, share, _ = expected()
    assert abs(float(out["import_content_share"]) - share) < 1e-5


def test_gfcf_total(out):
    _, tot, _, _ = expected()
    assert abs(float(out["gfcf_total"]) - tot) < 0.06


def test_top_contributor(out):
    _, _, _, top = expected()
    assert str(out["top_import_contributor"]).strip() == top


def test_ratios(out):
    ratios, _, _, _ = expected()
    got = out["import_ratios"]
    assert set(got.keys()) == set(ratios.keys())
    for c, v in ratios.items():
        assert abs(float(got[c]) - v) < 1e-5, c
