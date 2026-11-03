#!/bin/bash
set -e
cd /root/work
cat > /tmp/ref.py << 'EOF'

import csv, json

def even_down(x):
    return int(x) // 2 * 2

def solve(work):
    plats = json.load(open(f"{work}/platforms.json"))
    out = []
    for r in csv.DictReader(open(f"{work}/sources.csv")):
        W, H = int(r["width"]), int(r["height"])
        for p in plats:
            aw, ah = [int(x) for x in p["aspect"].split(":")]
            if W * ah > H * aw:
                ch = even_down(H); cw = even_down(H * aw // ah)
            else:
                cw = even_down(W); ch = even_down(W * ah // aw)
            cx, cy = even_down((W - cw) // 2), even_down((H - ch) // 2)
            ow = p["out_width"]
            if p.get("no_upscale") and cw < ow:
                ow = cw
            oh = even_down((2 * ow * ah + aw) // (2 * aw))
            out.append({"source_id": r["source_id"], "platform": p["name"], "crop_x": cx, "crop_y": cy,
                        "crop_w": cw, "crop_h": ch, "out_w": ow, "out_h": oh})
    return out

def write(work):
    rows = solve(work)
    with open(f"{work}/crops.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

write('/root/work')
EOF
python3 /tmp/ref.py
