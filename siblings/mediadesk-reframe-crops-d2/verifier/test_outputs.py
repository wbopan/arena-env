import json
import os

WORK = "/root/work"
OUT = os.path.join(WORK, 'crops.csv')

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

import csv as _csv

def test_output_exists():
    assert os.path.exists(OUT)

def test_rows():
    got = list(_csv.DictReader(open(OUT)))
    exp = solve(WORK)
    assert len(got) == len(exp)
    for g, x in zip(got, exp):
        assert g["source_id"].strip() == x["source_id"] and g["platform"].strip() == x["platform"]

def test_geometry():
    got = list(_csv.DictReader(open(OUT)))
    exp = solve(WORK)
    for g, x in zip(got, exp):
        for k in ("crop_x", "crop_y", "crop_w", "crop_h", "out_w", "out_h"):
            assert int(float(g[k])) == x[k], (x["source_id"], x["platform"], k)
