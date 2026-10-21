import csv
import cmath
import json
import math
import os

import pytest

OUT = "/root/work/branch_flows.csv"
NET = "/root/work/network.json"
HEADER = ["from_bus", "to_bus", "p_from_MW", "q_from_MVAr", "p_to_MW", "q_to_MVAr", "loss_MW", "loading_pct"]
TOL = 2e-3


def expected():
    net = json.load(open(NET))
    base = float(net["baseMVA"])
    V = {int(b[0]): cmath.rect(b[7], math.radians(b[8])) for b in net["bus"]}
    rows = []
    for br in net["branch"]:
        if int(br[10]) != 1:
            continue
        f, t = int(br[0]), int(br[1])
        y = 1.0 / complex(br[2], br[3])
        bc = br[4]
        tap = br[8] if br[8] != 0 else 1.0
        N = tap * cmath.exp(1j * math.radians(br[9]))
        Ytt = y + 1j * bc / 2
        Yff = Ytt / (tap * tap)
        Yft = -y / N.conjugate()
        Ytf = -y / N
        If = Yff * V[f] + Yft * V[t]
        It = Ytf * V[f] + Ytt * V[t]
        Sf = V[f] * If.conjugate() * base
        St = V[t] * It.conjugate() * base
        rate = br[5]
        load = 100 * max(abs(Sf), abs(St)) / rate if rate > 0 else 0.0
        rows.append([f, t, Sf.real, Sf.imag, St.real, St.imag, Sf.real + St.real, load])
    return rows


def read_out():
    with open(OUT) as fh:
        return list(csv.reader(fh))


def test_exists():
    assert os.path.isfile(OUT)


def test_header():
    rows = read_out()
    assert [h.strip() for h in rows[0]] == HEADER


def test_rows_and_order():
    rows = [r for r in read_out()[1:] if r]
    exp = expected()
    assert len(rows) == len(exp)
    for r, e in zip(rows, exp):
        assert int(float(r[0])) == e[0] and int(float(r[1])) == e[1]


def test_flows():
    rows = [r for r in read_out()[1:] if r]
    for r, e in zip(rows, expected()):
        for j in range(2, 6):
            assert abs(float(r[j]) - e[j]) <= TOL, (r, e)


def test_loss_and_loading():
    rows = [r for r in read_out()[1:] if r]
    for r, e in zip(rows, expected()):
        assert abs(float(r[6]) - e[6]) <= TOL, (r, e)
        assert abs(float(r[7]) - e[7]) <= TOL, (r, e)
