import json
import os
import re
import shlex
import glob
from fractions import Fraction

import numpy as np
import pytest

CIF_DIR = "/root/work/cifs"
OUT = "/root/work/wyckoff_summary.json"


def read_loops(path):
    lines = open(path).read().splitlines()
    loops = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == "loop_":
            i += 1
            hdr = []
            while i < len(lines) and lines[i].strip().startswith("_"):
                hdr.append(lines[i].strip())
                i += 1
            rows = []
            while i < len(lines):
                t = lines[i].strip()
                if not t or t == "loop_" or t.startswith("_") or t.startswith("data_"):
                    break
                rows.append(shlex.split(t))
                i += 1
            loops.append((hdr, rows))
        else:
            i += 1
    return loops


def num(s):
    return float(re.sub(r"\(.*?\)", "", s))


def expected_for(path):
    loops = read_loops(path)
    ops, atoms = None, None
    for hdr, rows in loops:
        if "_symmetry_equiv_pos_as_xyz" in hdr:
            k = hdr.index("_symmetry_equiv_pos_as_xyz")
            ops = [[c.strip() for c in r[k].split(",")] for r in rows]
        if "_atom_site_label" in hdr:
            atoms = [dict(zip(hdr, r)) for r in rows]
    sites = {}
    content = {}
    for a in atoms:
        p0 = [num(a["_atom_site_fract_" + ax]) for ax in "xyz"]
        imgs = []
        for op in ops:
            env = {"x": p0[0], "y": p0[1], "z": p0[2]}
            p = np.array([eval(c, {"__builtins__": {}}, env) for c in op]) % 1.0
            dup = False
            for q in imgs:
                d = p - q
                d -= np.round(d)
                if np.all(np.abs(d) < 1e-3):
                    dup = True
                    break
            if not dup:
                imgs.append(p)
        m = len(imgs)
        occ = num(a.get("_atom_site_occupancy", "1"))
        el = a["_atom_site_type_symbol"]
        content[el] = content.get(el, 0.0) + m * occ
        sites[a["_atom_site_label"]] = {"multiplicity": m, "reduced": [v % 1.0 for v in p0]}
    return {"n_symops": len(ops), "sites": sites,
            "cell_content": {k: round(v, 3) for k, v in content.items()}}


@pytest.fixture(scope="module")
def expected():
    return {os.path.basename(p): expected_for(p) for p in sorted(glob.glob(os.path.join(CIF_DIR, "*.cif")))}


@pytest.fixture(scope="module")
def result():
    assert os.path.exists(OUT), "output file missing"
    with open(OUT) as fh:
        return json.load(fh)


def test_file_and_keys(result, expected):
    assert isinstance(result, dict)
    assert set(result.keys()) == set(expected.keys())


def test_n_symops(result, expected):
    for f, e in expected.items():
        assert int(result[f]["n_symops"]) == e["n_symops"], f


def test_multiplicities(result, expected):
    for f, e in expected.items():
        sites = result[f]["sites"]
        assert set(sites.keys()) == set(e["sites"].keys()), f
        for lab, s in e["sites"].items():
            assert int(sites[lab]["multiplicity"]) == s["multiplicity"], (f, lab)


def test_fractions(result, expected):
    for f, e in expected.items():
        for lab, s in e["sites"].items():
            got = result[f]["sites"][lab]["fract"]
            assert len(got) == 3, (f, lab)
            for g, v in zip(got, s["reduced"]):
                assert isinstance(g, str), (f, lab, g)
                fr = Fraction(g.strip())
                assert fr.denominator <= 12, (f, lab, g)
                best = Fraction(v).limit_denominator(12)
                assert abs(float(fr) - v) <= abs(float(best) - v) + 1e-9, (f, lab, g, str(best))


def test_cell_content(result, expected):
    for f, e in expected.items():
        got = result[f]["cell_content"]
        assert set(got.keys()) == set(e["cell_content"].keys()), f
        for el, v in e["cell_content"].items():
            assert abs(float(got[el]) - v) <= 1e-3, (f, el, got[el], v)
