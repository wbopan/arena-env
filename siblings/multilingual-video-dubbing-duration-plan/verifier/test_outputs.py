import csv
import json
import os

import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "dub_plan.json")
KEYS = {"index", "window_start_sec", "window_end_sec", "window_duration_sec", "tts_duration_sec",
        "duration_control", "tempo_factor", "trimmed_sec", "speech_end_sec", "target_text"}
TOL = 0.002


def to_sec(s):
    hms, ms = s.strip().split(",")
    h, m, sec = hms.split(":")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000.0


def read_srt(path):
    with open(path, encoding="utf-8") as f:
        txt = f.read().replace("\r\n", "\n")
    cues = {}
    for block in txt.strip().split("\n\n"):
        lines = block.strip().split("\n")
        if len(lines) < 2:
            continue
        a, b = lines[1].split("-->")
        cues[int(lines[0].strip())] = (to_sec(a), to_sec(b), " ".join(l.strip() for l in lines[2:]).strip())
    return cues


def expected():
    win = read_srt(os.path.join(WORK, "segments.srt"))
    txt = read_srt(os.path.join(WORK, "target_text.srt"))
    tts = {}
    with open(os.path.join(WORK, "tts_durations.csv")) as f:
        for row in csv.DictReader(f):
            tts[int(row["segment_index"])] = float(row["tts_duration_sec"])
    with open(os.path.join(WORK, "target_language.txt")) as f:
        lang = f.read().strip()
    segs = []
    counts = {"pad_silence": 0, "rate_adjust": 0, "trim": 0}
    total = 0.0
    for idx in sorted(win, key=lambda k: win[k][0]):
        s, e, _ = win[idx]
        w = e - s
        d = tts[idx]
        r = d / w
        if r <= 1:
            ctrl, tf, tr, se = "pad_silence", 1.0, 0.0, s + d
        elif r <= 1.25:
            ctrl, tf, tr, se = "rate_adjust", r, 0.0, e
        else:
            ctrl, tf, tr, se = "trim", 1.25, d / 1.25 - w, e
        counts[ctrl] += 1
        total += tr
        segs.append({"index": idx, "window_start_sec": s, "window_end_sec": e, "window_duration_sec": w,
                     "tts_duration_sec": d, "duration_control": ctrl, "tempo_factor": tf,
                     "trimmed_sec": tr, "speech_end_sec": se, "target_text": txt[idx][2]})
    counts["total_trimmed_sec"] = total
    return lang, segs, counts


def load():
    with open(OUT, encoding="utf-8") as f:
        return json.load(f)


def test_file_exists_and_is_json():
    assert os.path.exists(OUT), "dub_plan.json missing"
    data = load()
    assert isinstance(data, dict)
    for k in ("target_language", "segments", "summary"):
        assert k in data, f"missing key {k}"


def test_schema_and_order():
    data = load()
    _, segs, _ = expected()
    assert len(data["segments"]) == len(segs)
    for got, exp in zip(data["segments"], segs):
        assert KEYS.issubset(got.keys()), f"missing keys in {got}"
        assert int(got["index"]) == exp["index"], "segments not in window order"


def test_duration_controls():
    data = load()
    _, segs, _ = expected()
    for got, exp in zip(data["segments"], segs):
        assert got["duration_control"] == exp["duration_control"], f"segment {exp['index']}"


def test_numeric_values():
    data = load()
    _, segs, _ = expected()
    for got, exp in zip(data["segments"], segs):
        for k in ("window_start_sec", "window_end_sec", "window_duration_sec", "tts_duration_sec",
                  "tempo_factor", "trimmed_sec", "speech_end_sec"):
            assert abs(float(got[k]) - exp[k]) <= TOL, f"segment {exp['index']} {k}: {got[k]} vs {exp[k]:.4f}"


def test_summary_text_language():
    data = load()
    lang, segs, counts = expected()
    assert data["target_language"] == lang
    for got, exp in zip(data["segments"], segs):
        assert got["target_text"].strip() == exp["target_text"], f"text of segment {exp['index']}"
    summ = data["summary"]
    for k in ("pad_silence", "rate_adjust", "trim"):
        assert int(summ[k]) == counts[k], k
    assert abs(float(summ["total_trimmed_sec"]) - counts["total_trimmed_sec"]) <= TOL
