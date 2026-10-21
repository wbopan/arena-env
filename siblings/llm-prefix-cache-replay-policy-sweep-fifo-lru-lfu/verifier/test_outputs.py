import json
import os
from collections import OrderedDict

import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "policy_comparison.json")


def simulate(trace, bs, cap, policy):
    res = OrderedDict()  # key -> [freq, admit_seq]
    seq = 0
    ev = 0
    hits = 0
    for r in trace:
        ids = r["hash_ids"]
        k = 0
        while k < len(ids) and ids[k] in res:
            k += 1
        hits += min(k * bs, r["input_length"])
        for h in ids:
            if h in res:
                if policy == "LRU":
                    res.move_to_end(h)
                elif policy == "LFU":
                    res[h][0] += 1
            else:
                if len(res) >= cap:
                    if policy == "LFU":
                        victim = min(res, key=lambda x: (res[x][0], res[x][1]))
                        del res[victim]
                    else:
                        res.popitem(last=False)
                    ev += 1
                seq += 1
                res[h] = [1, seq]
    return hits, ev, len(res)


@pytest.fixture(scope="module")
def setup():
    with open(os.path.join(WORK, "config.json")) as f:
        cfg = json.load(f)
    with open(os.path.join(WORK, "trace.jsonl")) as f:
        trace = [json.loads(x) for x in f if x.strip()]
    total = sum(r["input_length"] for r in trace)
    exp = {}
    for p in cfg["policies"]:
        exp[p] = {}
        for c in cfg["capacities"]:
            h, e, fb = simulate(trace, cfg["block_size"], c, p)
            exp[p][str(c)] = {"hit_tokens": h, "hit_rate": round(h / total, 6),
                              "evictions": e, "final_cache_blocks": fb}
    return cfg, len(trace), total, exp


@pytest.fixture(scope="module")
def actual():
    assert os.path.exists(OUT), "policy_comparison.json not created"
    with open(OUT) as f:
        return json.load(f)


def test_schema(actual, setup):
    cfg = setup[0]
    for key in ("total_requests", "total_prompt_tokens", "results"):
        assert key in actual, f"missing {key}"
    for p in cfg["policies"]:
        assert p in actual["results"], f"missing policy {p}"
        for c in cfg["capacities"]:
            ent = actual["results"][p][str(c)]
            for f in ("hit_tokens", "hit_rate", "evictions", "final_cache_blocks"):
                assert f in ent, f"missing {p}/{c}/{f}"


def test_totals(actual, setup):
    assert actual["total_requests"] == setup[1]
    assert actual["total_prompt_tokens"] == setup[2]


def test_hit_tokens(actual, setup):
    exp = setup[3]
    for p in exp:
        for c in exp[p]:
            assert actual["results"][p][c]["hit_tokens"] == exp[p][c]["hit_tokens"], \
                f"{p} cap={c}: got {actual['results'][p][c]['hit_tokens']} want {exp[p][c]['hit_tokens']}"


def test_hit_rate(actual, setup):
    exp = setup[3]
    for p in exp:
        for c in exp[p]:
            assert abs(actual["results"][p][c]["hit_rate"] - exp[p][c]["hit_rate"]) <= 1.5e-6, f"{p} cap={c}"


def test_evictions_and_final(actual, setup):
    exp = setup[3]
    for p in exp:
        for c in exp[p]:
            a = actual["results"][p][c]
            assert a["evictions"] == exp[p][c]["evictions"], f"{p} cap={c} evictions"
            assert a["final_cache_blocks"] == exp[p][c]["final_cache_blocks"], f"{p} cap={c} final"
