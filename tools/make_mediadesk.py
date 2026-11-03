#!/usr/bin/env python3
"""
Write procedural media task families as sibling task directories (task.json, gen_data.py,
verifier/test_outputs.py, oracle/solve.sh), in the layout tools/build_mini.py serves.

Each family has one reference implementation (REF) that both the oracle and the verifier use:
the oracle writes REF's output, the verifier recomputes it from the episode's inputs and
compares. gen_data.py seeds `random` with a constant, so the arena runtime's seeded runner
gives every episode a fresh instance.

    make_mediadesk.py OUT_DIR
"""

import json
import sys
import textwrap
from pathlib import Path

CATEGORY = "media-content-production"

# ---------------------------------------------------------------- subtitle retime
SRT_COMMON = r'''
import json, re

def parse_ts(s):
    h, m, rest = s.strip().split(":")
    sec, ms = rest.split(",")
    return ((int(h) * 60 + int(m)) * 60 + int(sec)) * 1000 + int(ms)

def fmt_ts(ms):
    return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)

def parse_srt(text):
    cues = []
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip()):
        lines = block.strip("\n").split("\n")
        if len(lines) < 2 or "-->" not in lines[1]:
            continue
        a, b = lines[1].split("-->")
        cues.append((int(lines[0].strip()), parse_ts(a), parse_ts(b), [l.rstrip() for l in lines[2:]]))
    return cues
'''

SRT_REF = SRT_COMMON + r'''
def solve(work):
    job = json.load(open(f"{work}/job.json"))
    cues = parse_srt(open(f"{work}/input.srt", encoding="utf-8").read())
    cues.sort(key=lambda c: c[0])
    num, den = job.get("scale_num", 1), job.get("scale_den", 1)
    off = job["offset_ms"]
    out = []
    for _, s, e, txt in cues:
        s2 = (2 * s * num + den) // (2 * den) + off
        e2 = (2 * e * num + den) // (2 * den) + off
        if e2 <= 0:
            continue
        out.append([max(s2, 0), e2, txt])
    gap = job.get("min_gap_ms")
    if gap:
        for i in range(len(out) - 1):
            if out[i + 1][0] - out[i][1] < gap:
                out[i][1] = out[i + 1][0] - gap
    return [(i + 1, s, e, t) for i, (s, e, t) in enumerate(out)]

def write(work):
    with open(f"{work}/output.srt", "w", encoding="utf-8") as f:
        f.write("\n".join("%d\n%s --> %s\n%s\n" % (i, fmt_ts(s), fmt_ts(e), "\n".join(t)) for i, s, e, t in solve(work)))
'''

SRT_GEN = r'''
import json, random
random.seed({seed})
LEVEL = {level}
LINES = ["Welcome back to the workshop.", "Today we restore an old radio.", "First, unplug everything.",
         "Check the capacitors for bulges.", "This one has clearly failed.", "We desolder it carefully.",
         "Mind the polarity on the new part.", "Now the dial cord is next.", "It slips on the pulley.",
         "A drop of glue fixes that.", "Let us power it up slowly.", "Hear that? It hums again.",
         "The tuning is a little off.", "Adjust the trimmer by a hair.", "Much better now.",
         "Thanks for watching, see you soon.", "Subscribe for the next build.", "Bring your own radios!"]
def fmt(ms):
    return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)
n = random.randint(12, 18)
t = random.randint(300, 2500)
cues = []
for i in range(n):
    if LEVEL >= 3 and random.random() < 0.35:
        t += random.randint(10, 70)
    else:
        t += random.randint(150, 900)
    d = random.randint(900, 3400)
    txt = [LINES[i % len(LINES)]]
    if random.random() < 0.3:
        txt.append("(" + random.choice(["music", "laughs", "static", "door closes"]) + ")")
    cues.append((i + 1, t, t + d, txt))
    t += d
order = list(range(n))
if LEVEL >= 2:
    k = random.randint(2, n - 3)
    order[k], order[k + 1] = order[k + 1], order[k]
with open("input.srt", "w", encoding="utf-8") as f:
    f.write("\n".join("%d\n%s --> %s\n%s\n" % (cues[j][0], fmt(cues[j][1]), fmt(cues[j][2]), "\n".join(cues[j][3])) for j in order))
job = {{"offset_ms": random.choice([-1, 1]) * random.randint(400, 2600)}}
if job["offset_ms"] < 0 and random.random() < 0.6:
    job["offset_ms"] = -(cues[0][2] + random.randint(50, 400))
if LEVEL >= 2:
    job["source_fps"], job["target_fps"] = "23.976", "25"
    job["scale_num"], job["scale_den"] = 24000, 25025
if LEVEL >= 3:
    job["min_gap_ms"] = 80
json.dump(job, open("job.json", "w"), indent=1)
'''

SRT_INSTR = {
    1: """# Re-time a subtitle file

`/root/work/input.srt` is an SRT subtitle file and `/root/work/job.json` holds `offset_ms`, a shift in milliseconds (it can be negative).

Write `/root/work/output.srt`: every timestamp moved by `offset_ms`. A cue whose new end is at or before 00:00:00,000 is removed; a cue whose new start is negative starts at 00:00:00,000. Keep each cue's text lines unchanged and in order. Number the remaining cues 1, 2, 3, ... in order. Use the format `HH:MM:SS,mmm --> HH:MM:SS,mmm` and separate cues with one blank line.""",
    2: """# Convert subtitles to a new frame rate

`/root/work/input.srt` was timed against a 23.976 fps master. The new master is the same picture played at 25 fps, so every moment comes earlier by the factor 24000/25025. `/root/work/job.json` also gives `offset_ms`, a shift in milliseconds applied after the conversion (it can be negative). The input cues are not all in index order: process them by their cue index.

Write `/root/work/output.srt`. For every timestamp t (in milliseconds) of the input: new = t x 24000 / 25025 rounded to the nearest millisecond (halves round up), then plus `offset_ms`. Convert each timestamp from its original value, never from an earlier result. A cue whose new end is at or before zero is removed; a negative new start becomes 00:00:00,000. Keep the text lines unchanged. Number the remaining cues 1, 2, 3, ... by original index order. Format `HH:MM:SS,mmm --> HH:MM:SS,mmm`, one blank line between cues.""",
    3: """# Conform subtitles to a new master

`/root/work/input.srt` was timed against a 23.976 fps master; the new master is the same picture at 25 fps, so every moment comes earlier by the factor 24000/25025. `/root/work/job.json` gives `offset_ms` (applied after the conversion, can be negative) and `min_gap_ms`. The input cues are not all in index order: process them by cue index.

Write `/root/work/output.srt`:
1. For every timestamp t in milliseconds: new = t x 24000 / 25025 rounded to the nearest millisecond (halves round up), plus `offset_ms`. Always convert from the original value.
2. Remove cues whose new end is at or before zero; a negative new start becomes 0.
3. Then, going through the remaining cues in index order, if the next cue starts less than `min_gap_ms` after a cue ends, move that cue's end earlier to exactly `min_gap_ms` before the next cue's start. Starts never move.
4. Number the cues 1, 2, 3, ...; keep text lines unchanged. Format `HH:MM:SS,mmm --> HH:MM:SS,mmm`, one blank line between cues.""",
}

SRT_CHECK = r'''
def test_output_exists():
    assert os.path.exists(OUT)

def test_cue_count_and_numbering():
    got = parse_srt(open(OUT, encoding="utf-8").read())
    exp = solve(WORK)
    assert len(got) == len(exp)
    assert [c[0] for c in got] == list(range(1, len(exp) + 1))

def test_timestamps():
    got = parse_srt(open(OUT, encoding="utf-8").read())
    exp = solve(WORK)
    for g, x in zip(got, exp):
        assert abs(g[1] - x[1]) <= 1 and abs(g[2] - x[2]) <= 1, (g[0], g[1], g[2], x[1], x[2])

def test_text():
    got = parse_srt(open(OUT, encoding="utf-8").read())
    exp = solve(WORK)
    for g, x in zip(got, exp):
        assert [l.strip() for l in g[3]] == [l.strip() for l in x[3]]
'''

# ---------------------------------------------------------------- timecode / EDL
TC_REF = r'''
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
'''

TC_GEN = r'''
import csv, json, random
random.seed({seed})
LEVEL = {level}
''' + TC_REF.split("def solve")[0].split("import csv, json")[1] + r'''
fps = {{1: 25, 2: 30, 3: 30}}[LEVEL]
drop = LEVEL == 3
rows = []
for i in range(random.randint(8, 14)):
    start = random.randint(0, 3 * 3600 * fps) if not drop else random.randint(0, 107892 * 2)
    if drop and random.random() < 0.5:
        mm = random.randint(1, 59)
        if mm % 10 == 0:
            mm += 1
        start = tc_to_frames("%02d:%02d:59;%02d" % (random.randint(0, 1), mm - 1, random.randint(20, 29)), 30, True)
    length = random.randint(2 * fps, 40 * fps)
    status = "keep"
    if LEVEL >= 2 and random.random() < 0.25:
        status = "skip"
    rows.append({{"clip_id": "C%03d" % (i + 1), "reel": "R%d" % random.randint(1, 4),
                 "src_in": frames_to_tc(start, fps, drop), "src_out": frames_to_tc(start + length, fps, drop), "status": status}})
fields = ["clip_id", "reel", "src_in", "src_out"] + (["status"] if LEVEL >= 2 else [])
with open("edl.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
json.dump({{"fps": fps, "drop_frame": drop}}, open("job.json", "w"))
'''

TC_INSTR = {
    1: """# Edit list runtime

`/root/work/edl.csv` lists the clips of an edit with source timecodes `src_in` and `src_out` (SMPTE `HH:MM:SS:FF`). `/root/work/job.json` gives the frame rate `fps` (non-drop). `src_out` is exclusive: a clip from 00:00:01:00 to 00:00:02:00 at 25 fps is 25 frames.

Write `/root/work/runtime.json` as `{"clips": [{"clip_id": ..., "frames": ...}, ...], "total_frames": N, "total_timecode": "HH:MM:SS:FF"}`: clips in file order with their length in frames (integers), the sum of all lengths, and that sum as a timecode at the same rate counted from 00:00:00:00.""",
    2: """# Edit list runtime

`/root/work/edl.csv` lists the clips of an edit with source timecodes `src_in` and `src_out` (SMPTE `HH:MM:SS:FF`) and a `status`. `/root/work/job.json` gives the frame rate `fps` (non-drop). `src_out` is exclusive: 00:00:01:00 to 00:00:02:00 at 30 fps is 30 frames. Clips whose status is `skip` are not in the cut.

Write `/root/work/runtime.json` as `{"clips": [{"clip_id": ..., "frames": ...}, ...], "total_frames": N, "total_timecode": "HH:MM:SS:FF"}`: the clips in the cut, in file order, with their lengths in frames (integers), the sum, and the sum as a timecode at the same rate counted from 00:00:00:00.""",
    3: """# Drop-frame edit list runtime

`/root/work/edl.csv` lists clips with source timecodes `src_in` and `src_out` in 29.97 fps drop-frame SMPTE timecode (`HH:MM:SS;FF`), and a `status`; `skip` clips are not in the cut. `src_out` is exclusive. Drop-frame numbering skips frame labels 00 and 01 at the start of every minute except minutes divisible by 10 (no frames are actually dropped), so the frame count between two labels is not the naive difference.

Write `/root/work/runtime.json` as `{"clips": [{"clip_id": ..., "frames": ...}, ...], "total_frames": N, "total_timecode": "HH:MM:SS;FF"}`: the clips in the cut in file order with their true lengths in frames, the sum, and the sum as a drop-frame timecode counted from 00:00:00;00.""",
}

TC_CHECK = r'''
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
'''

# ---------------------------------------------------------------- catalogue
CAT_REF = r'''
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
'''

CAT_GEN = r'''
import csv, json, random
random.seed({seed})
LEVEL = {level}
WORDS = ["harbour", "night", "signal", "orchard", "glass", "river", "atlas", "ember", "quiet", "north", "copper", "tide"]
def fmt(sec):
    h, m, s = sec // 3600, sec // 60 % 60, sec % 60
    k = random.randrange(4)
    if k == 0:
        return "%d:%02d:%02d" % (h, m, s)
    if k == 1 and h == 0:
        return "%d:%02d" % (m, s)
    if k == 2:
        return "%ds" % sec
    return (("%dh" % h) if h else "") + (("%dm" % m) if m else "") + (("%ds" % s) if s or not (h or m) else "")
rows = []
n = random.randint(9, 14)
for i in range(n):
    aid = "MA-%04d" % random.randint(100, 9999)
    title = " ".join(random.sample(WORDS, random.randint(1, 3))).title()
    if random.random() < 0.4:
        title = "  " + title.replace(" ", "   ") + " "
    sec = random.randint(25, 5400) if random.random() < 0.8 else random.choice([60, 3600, 600])
    rows.append([aid if random.random() < 0.7 else aid.lower(), title, fmt(sec), "2026-%02d-%02dT%02d:00:00Z" % (random.randint(1, 9), random.randint(1, 28), random.randint(0, 23))])
if LEVEL >= 2:
    for _ in range(random.randint(2, 4)):
        r = list(random.choice(rows))
        r[0] = r[0].upper() if random.random() < 0.5 else r[0].lower()
        r[2] = fmt(random.randint(25, 5400))
        r[3] = "2026-%02d-%02dT%02d:00:00Z" % (random.randint(1, 9), random.randint(1, 28), random.randint(0, 23))
        rows.append(r)
random.shuffle(rows)
with open("library.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["asset_id", "title", "duration", "updated_at"]); w.writerows(rows)
job = {{}}
if LEVEL >= 2:
    job["playlist_cap_sec"] = random.randint(1800, 7200)
json.dump(job, open("job.json", "w"))
'''

CAT_INSTR = {
    1: """# Normalise a media catalogue

`/root/work/library.csv` has columns `asset_id, title, duration, updated_at`. Durations come in mixed forms: `H:MM:SS`, `M:SS`, `<n>s` and `<h>h<m>m<s>s` with any part omitted (for example `1h5s`, `42m`). Asset ids are case-insensitive. Every id occurs once.

Write `/root/work/catalog.json` as `{"items": [...]}` with one item per asset, sorted by upper-case id: `{"asset_id": upper-case id, "title": title with surrounding spaces removed and inner runs of spaces collapsed to one, "duration": ISO 8601 duration, "duration_sec": integer seconds}`. The ISO form is `PT` followed by hours `H`, minutes `M` and seconds `S`, leaving out zero parts (`PT1H5S`, `PT42M`); zero is `PT0S`.""",
    2: """# Normalise a media catalogue and build a playlist

`/root/work/library.csv` has columns `asset_id, title, duration, updated_at`. Durations come in mixed forms: `H:MM:SS`, `M:SS`, `<n>s` and `<h>h<m>m<s>s` with any part omitted (for example `1h5s`, `42m`). Asset ids are case-insensitive, and some assets appear more than once: keep only the row with the latest `updated_at` (ISO timestamps). `/root/work/job.json` gives `playlist_cap_sec`.

Write `/root/work/catalog.json` with:
- `items`: one item per asset, sorted by upper-case id: `{"asset_id": upper-case id, "title": trimmed with inner space runs collapsed to one, "duration": ISO 8601 duration, "duration_sec": integer seconds}`. The ISO form is `PT` then hours `H`, minutes `M`, seconds `S`, leaving out zero parts (`PT1H5S`, `PT42M`); zero is `PT0S`.
- `playlist`: asset ids chosen greedily: go through the items from shortest to longest (ties by id) and add each one whose duration still fits so the total stays at or under `playlist_cap_sec`; skip ones that do not fit and keep going.
- `playlist_sec`: the playlist's total seconds.""",
}

CAT_CHECK = r'''
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
'''

# ---------------------------------------------------------------- reframe / crop
CROP_REF = r'''
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
'''

CROP_GEN = r'''
import csv, json, random
random.seed({seed})
LEVEL = {level}
sizes = [(3840, 2160), (1920, 1080), (1280, 720), (4096, 1716), (1440, 1080), (2048, 858), (1080, 1920), (3000, 2000), (720, 576)]
rows = []
for i in range(random.randint(4, 7)):
    W, H = random.choice(sizes)
    if random.random() < 0.4:
        W += random.choice([-6, 2, 10, 14]); H += random.choice([-2, 6, 12])
    rows.append(["SRC%02d" % (i + 1), W, H])
with open("sources.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["source_id", "width", "height"]); w.writerows(rows)
plats = [{{"name": "vertical", "aspect": "9:16", "out_width": 1080}}, {{"name": "square", "aspect": "1:1", "out_width": 1080}},
         {{"name": "feed", "aspect": "4:5", "out_width": 1080}}, {{"name": "wide", "aspect": "16:9", "out_width": 1920}},
         {{"name": "cinema", "aspect": "21:9", "out_width": 2560}}]
plats = random.sample(plats, random.randint(2, 4))
if LEVEL >= 2:
    for p in plats:
        p["no_upscale"] = True
json.dump(plats, open("platforms.json", "w"), indent=1)
'''

CROP_INSTR = {
    1: """# Reframe sources for social platforms

`/root/work/sources.csv` lists source videos (`source_id, width, height` in pixels) and `/root/work/platforms.json` lists target platforms with `name`, `aspect` (`w:h`) and `out_width`.

For every source and every platform (sources in file order, platforms in file order within each source) compute the largest centred crop with the platform's aspect: if the source is wider than the aspect, crop_h = H and crop_w = floor(H x aw / ah); otherwise crop_w = W and crop_h = floor(W x ah / aw). Then round crop_w and crop_h down to even numbers. crop_x = floor((W - crop_w) / 2) and crop_y = floor((H - crop_h) / 2), each also rounded down to even. The output size is out_w = `out_width` and out_h = out_w x ah / aw rounded to the nearest integer (halves up) and then down to even.

Write `/root/work/crops.csv` with header `source_id,platform,crop_x,crop_y,crop_w,crop_h,out_w,out_h`, integers only.""",
    2: """# Reframe sources for social platforms without upscaling

`/root/work/sources.csv` lists source videos (`source_id, width, height` in pixels) and `/root/work/platforms.json` lists target platforms with `name`, `aspect` (`w:h`), `out_width` and `no_upscale`.

For every source and every platform (sources in file order, platforms in file order within each source) compute the largest centred crop with the platform's aspect: if the source is wider than the aspect, crop_h = H and crop_w = floor(H x aw / ah); otherwise crop_w = W and crop_h = floor(W x ah / aw). Round crop_w and crop_h down to even. crop_x = floor((W - crop_w) / 2) and crop_y = floor((H - crop_h) / 2), each rounded down to even. out_w is `out_width`, except that with `no_upscale` true and crop_w smaller than `out_width`, out_w = crop_w. out_h = out_w x ah / aw rounded to the nearest integer (halves up), then down to even.

Write `/root/work/crops.csv` with header `source_id,platform,crop_x,crop_y,crop_w,crop_h,out_w,out_h`, integers only.""",
}

CROP_CHECK = r'''
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
'''

FAMILIES = [
    ("mediadesk-subtitle-retime", SRT_REF, SRT_GEN, SRT_INSTR, SRT_CHECK, "output.srt", "subtitles"),
    ("mediadesk-edl-runtime", TC_REF, TC_GEN, TC_INSTR, TC_CHECK, "runtime.json", "timecode"),
    ("mediadesk-catalog-normalize", CAT_REF, CAT_GEN, CAT_INSTR, CAT_CHECK, "catalog.json", "catalogue"),
    ("mediadesk-reframe-crops", CROP_REF, CROP_GEN, CROP_INSTR, CROP_CHECK, "crops.csv", "reframing"),
]

VERIFIER_HEAD = """import json
import os

WORK = "/root/work"
OUT = os.path.join(WORK, {out!r})
"""


def main() -> int:
    out = Path(sys.argv[1])
    for name, ref, gen, instr, check, outfile, source in FAMILIES:
        for level, text in instr.items():
            d = out / f"{name}-d{level}"
            (d / "verifier").mkdir(parents=True, exist_ok=True)
            (d / "oracle").mkdir(exist_ok=True)
            seed = 20261103 + 97 * level + 13 * len(name)
            (d / "gen_data.py").write_text(gen.format(seed=seed, level=level).lstrip())
            (d / "verifier" / "test_outputs.py").write_text(VERIFIER_HEAD.format(out=outfile) + ref + "\n" + check.lstrip())
            (d / "oracle" / "solve.sh").write_text(
                "#!/bin/bash\nset -e\ncd /root/work\ncat > /tmp/ref.py << 'EOF'\n" + ref + "\nwrite('/root/work')\nEOF\npython3 /tmp/ref.py\n")
            (d / "oracle" / "solve.sh").chmod(0o755)
            (d / "requirements.txt").write_text("\n")
            (d / "task.json").write_text(json.dumps({
                "name": d.name, "source": f"mediadesk-{source}", "category": CATEGORY, "workdir": "/root/work",
                "instruction": text}, indent=1, ensure_ascii=False) + "\n")
            (d / "task.md").write_text(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
