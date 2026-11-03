#!/bin/bash
set -e
cd /root/work
cat > /tmp/ref.py << 'EOF'

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

write('/root/work')
EOF
python3 /tmp/ref.py
