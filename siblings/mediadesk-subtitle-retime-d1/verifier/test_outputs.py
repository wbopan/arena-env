import json
import os

WORK = "/root/work"
OUT = os.path.join(WORK, 'output.srt')

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
