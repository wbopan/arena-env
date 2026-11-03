import json
import os

WORK = "/root/work"
OUT = os.path.join(WORK, 'runtime.json')

import csv, json

def tc_to_frames(tc, fps, drop):
    sep = ";" if ";" in tc else ":"
    h, m, s, f = [int(x) for x in tc.replace(";", ":").split(":")]
    if not drop:
        return ((h * 60 + m) * 60 + s) * fps + f
    total_min = h * 60 + m
    return ((h * 3600 + m * 60 + s) * 30 + f) - 2 * (total_min - total_min // 10)

def frames_to_tc(n, fps, drop):
    if not drop:
        f = n % fps; s = n // fps
        return "%02d:%02d:%02d:%02d" % (s // 3600, s // 60 % 60, s % 60, f)
    d, m = divmod(n, 17982)
    n += 18 * d + (2 * ((m - 2) // 1798) if m >= 2 else 0)
    f = n % 30; s = n // 30
    return "%02d:%02d:%02d;%02d" % (s // 3600, s // 60 % 60, s % 60, f)

def solve(work):
    job = json.load(open(f"{work}/job.json"))
    fps, drop = job["fps"], job.get("drop_frame", False)
    clips, total = [], 0
    for r in csv.DictReader(open(f"{work}/edl.csv")):
        if r.get("status", "keep").strip().lower() == "skip":
            continue
        n = tc_to_frames(r["src_out"], fps, drop) - tc_to_frames(r["src_in"], fps, drop)
        clips.append({"clip_id": r["clip_id"].strip(), "frames": n})
        total += n
    return {"clips": clips, "total_frames": total, "total_timecode": frames_to_tc(total, fps, drop)}

def write(work):
    json.dump(solve(work), open(f"{work}/runtime.json", "w"), indent=1)

def load():
    return json.load(open(OUT))

def test_output_exists():
    assert os.path.exists(OUT)

def test_clips():
    got, exp = load(), solve(WORK)
    assert [c["clip_id"] for c in got["clips"]] == [c["clip_id"] for c in exp["clips"]]
    assert [int(c["frames"]) for c in got["clips"]] == [c["frames"] for c in exp["clips"]]

def test_total():
    got, exp = load(), solve(WORK)
    assert int(got["total_frames"]) == exp["total_frames"]
    assert got["total_timecode"].strip() == exp["total_timecode"]
