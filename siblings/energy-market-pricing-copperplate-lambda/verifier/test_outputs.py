import json
import os

import pytest
from scipy.optimize import brentq

WORK = "/root/work"
OUT = os.path.join(WORK, "dispatch.json")
NET = os.path.join(WORK, "network.json")


def compute_expected():
    with open(NET) as f:
        d = json.load(f)
    load = sum(float(b[2]) for b in d["bus"])
    units = []
    for k, (g, c) in enumerate(zip(d["gen"], d["gencost"])):
        if int(g[7]) == 1:
            units.append({"idx": k + 1, "bus": int(g[0]), "pmax": float(g[8]),
                          "pmin": float(g[9]), "c2": float(c[4]), "c1": float(c[5]),
                          "c0": float(c[6])})

    def p(u, lam):
        return min(max((lam - u["c1"]) / (2 * u["c2"]), u["pmin"]), u["pmax"])

    lam = brentq(lambda l: sum(p(u, l) for u in units) - load, 0.0, 1000.0, xtol=1e-12)
    cost = 0.0
    gens = []
    for u in units:
        pu = p(u, lam)
        cost += u["c2"] * pu * pu + u["c1"] * pu + u["c0"]
        if abs(pu - u["pmax"]) <= 0.01:
            lim = "pmax"
        elif abs(pu - u["pmin"]) <= 0.01:
            lim = "pmin"
        else:
            lim = "none"
        gens.append({"gen_index": u["idx"], "bus": u["bus"], "output_MW": pu, "at_limit": lim})
    return {"load": load, "lam": lam, "cost": cost, "gens": gens}


@pytest.fixture(scope="module")
def exp():
    return compute_expected()


@pytest.fixture(scope="module")
def rep():
    assert os.path.exists(OUT), "dispatch.json missing"
    with open(OUT) as f:
        return json.load(f)


def test_schema(rep):
    for key in ["total_load_MW", "system_lambda_dollars_per_MWh",
                "total_cost_dollars_per_hour", "generators"]:
        assert key in rep
    for g in rep["generators"]:
        for key in ["gen_index", "bus", "output_MW", "at_limit"]:
            assert key in g


def test_generator_list(rep, exp):
    got = [(int(g["gen_index"]), int(g["bus"])) for g in rep["generators"]]
    want = [(g["gen_index"], g["bus"]) for g in exp["gens"]]
    assert got == want


def test_lambda_and_load(rep, exp):
    assert abs(float(rep["total_load_MW"]) - exp["load"]) <= 0.05
    assert abs(float(rep["system_lambda_dollars_per_MWh"]) - exp["lam"]) <= 0.01


def test_outputs_and_balance(rep, exp):
    outs = [float(g["output_MW"]) for g in rep["generators"]]
    assert len(outs) == len(exp["gens"])
    for o, e in zip(outs, exp["gens"]):
        assert abs(o - e["output_MW"]) <= 0.05, (o, e)
    assert abs(sum(outs) - exp["load"]) <= 0.05


def test_cost(rep, exp):
    assert abs(float(rep["total_cost_dollars_per_hour"]) - exp["cost"]) <= 1.0


def test_at_limit(rep, exp):
    got = [g["at_limit"] for g in rep["generators"]]
    want = [g["at_limit"] for g in exp["gens"]]
    assert got == want
