import json
import os
import statistics

EN = "/root/work/energies.json"
PA = "/root/work/pauses.json"
OUT = "/root/work/compression_report.json"


def expected():
    with open(EN) as f:
        e = [float(v) for v in json.load(f)["energies"]]
    with open(PA) as f:
        pauses = json.load(f)["segments"]
    D = len(e)
    thr = 3 * statistics.median(e[:20])
    op = 0
    for i in range(D - 2):
        if e[i] > thr and e[i + 1] > thr and e[i + 2] > thr:
            op = i
            break
    raw = [(float(s["start"]), float(s["end"])) for s in pauses]
    if op > 0:
        raw.append((0.0, float(op)))
    clipped = sorted((max(0.0, s), min(float(D), t)) for s, t in raw)
    clipped = [c for c in clipped if c[1] > c[0]]
    merged = []
    for s, t in clipped:
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], t)
        else:
            merged.append([s, t])
    removed = sum(t - s for s, t in merged)
    return {
        "D": D,
        "op": op,
        "merged": merged,
        "removed": removed,
        "compressed": D - removed,
        "pct": round(removed / D * 100, 2),
    }


def load():
    with open(OUT) as f:
        return json.load(f)


def test_output_exists():
    assert os.path.isfile(OUT), "compression_report.json not found"
    assert isinstance(load(), dict)


def test_schema():
    d = load()
    for k in ("original_duration_seconds", "opening_end_seconds", "compressed_duration_seconds",
              "removed_duration_seconds", "compression_percentage", "segments_removed"):
        assert k in d, f"missing {k}"
    assert isinstance(d["segments_removed"], list) and len(d["segments_removed"]) > 0
    for s in d["segments_removed"]:
        for k in ("start", "end", "duration"):
            assert k in s
        assert abs(float(s["end"]) - float(s["start"]) - float(s["duration"])) < 1e-6


def test_opening_end():
    exp = expected()
    assert abs(float(load()["opening_end_seconds"]) - exp["op"]) < 1e-6


def test_segments_removed():
    exp = expected()
    got = [(float(s["start"]), float(s["end"])) for s in load()["segments_removed"]]
    assert len(got) == len(exp["merged"]), f"expected {len(exp['merged'])} segments, got {len(got)}"
    for (gs, ge), (es, ee) in zip(got, exp["merged"]):
        assert abs(gs - es) < 1e-6 and abs(ge - ee) < 1e-6, f"got {(gs, ge)} expected {(es, ee)}"


def test_totals():
    exp = expected()
    d = load()
    assert abs(float(d["original_duration_seconds"]) - exp["D"]) < 1e-6
    assert abs(float(d["removed_duration_seconds"]) - exp["removed"]) < 1e-6
    assert abs(float(d["compressed_duration_seconds"]) - exp["compressed"]) < 1e-6
    assert abs(float(d["compression_percentage"]) - exp["pct"]) <= 0.01
