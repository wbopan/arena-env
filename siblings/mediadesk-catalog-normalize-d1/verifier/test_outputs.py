import json
import os

WORK = "/root/work"
OUT = os.path.join(WORK, 'catalog.json')

import csv, json, re

def to_sec(d):
    d = d.strip().lower()
    m = re.fullmatch(r"(\d+):(\d{2}):(\d{2})", d)
    if m:
        return int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3])
    m = re.fullmatch(r"(\d+):(\d{2})", d)
    if m:
        return int(m[1]) * 60 + int(m[2])
    m = re.fullmatch(r"(\d+)\s*s(ec)?", d)
    if m:
        return int(m[1])
    m = re.fullmatch(r"(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:(\d+)s)?", d)
    if m and any(m.groups()):
        return int(m[1] or 0) * 3600 + int(m[2] or 0) * 60 + int(m[3] or 0)
    raise ValueError(d)

def iso(sec):
    h, m, s = sec // 3600, sec // 60 % 60, sec % 60
    out = "PT" + (f"{h}H" if h else "") + (f"{m}M" if m else "") + (f"{s}S" if s else "")
    return out if out != "PT" else "PT0S"

def solve(work):
    job = json.load(open(f"{work}/job.json"))
    best = {}
    for r in csv.DictReader(open(f"{work}/library.csv", encoding="utf-8")):
        aid = r["asset_id"].strip().upper()
        if aid in best and r["updated_at"] <= best[aid]["updated_at"]:
            continue
        best[aid] = r
    items = []
    for aid in sorted(best):
        r = best[aid]
        sec = to_sec(r["duration"])
        items.append({"asset_id": aid, "title": " ".join(r["title"].split()), "duration": iso(sec), "duration_sec": sec})
    out = {"items": items}
    if "playlist_cap_sec" in job:
        cap, total, pl = job["playlist_cap_sec"], 0, []
        for it in sorted(items, key=lambda x: (x["duration_sec"], x["asset_id"])):
            if total + it["duration_sec"] <= cap:
                pl.append(it["asset_id"]); total += it["duration_sec"]
        out["playlist"] = pl
        out["playlist_sec"] = total
    return out

def write(work):
    json.dump(solve(work), open(f"{work}/catalog.json", "w"), indent=1)

def load():
    return json.load(open(OUT, encoding="utf-8"))

def test_output_exists():
    assert os.path.exists(OUT)

def test_items():
    got, exp = load(), solve(WORK)
    assert [i["asset_id"] for i in got["items"]] == [i["asset_id"] for i in exp["items"]]
    for g, x in zip(got["items"], exp["items"]):
        assert int(g["duration_sec"]) == x["duration_sec"], x["asset_id"]
        assert g["duration"] == x["duration"], x["asset_id"]
        assert g["title"] == x["title"], x["asset_id"]

def test_playlist():
    got, exp = load(), solve(WORK)
    if "playlist" in exp:
        assert [p.upper() for p in got["playlist"]] == exp["playlist"]
        assert int(got["playlist_sec"]) == exp["playlist_sec"]
