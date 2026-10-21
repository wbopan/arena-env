import json
import os
import wave

import numpy as np

WAV = "/root/work/lecture_audio.wav"
OUT = "/root/work/pauses.json"


def expected():
    with wave.open(WAV, "rb") as w:
        sr = w.getframerate()
        raw = w.readframes(w.getnframes())
    x = np.frombuffer(raw, dtype="<i2").astype(np.float64)
    n = len(x) // sr
    e = np.sqrt(np.mean(x[: n * sr].reshape(n, sr) ** 2, axis=1))
    low = []
    for i in range(n):
        lo = max(0, i - 7)
        hi = min(n, i + 8)
        low.append(bool(e[i] < 0.5 * e[lo:hi].mean()))
    segs = []
    i = 0
    while i < n:
        if low[i]:
            j = i
            while j < n and low[j]:
                j += 1
            if j - i >= 2:
                segs.append((i, j))
            i = j
        else:
            i += 1
    return n, segs


def load():
    with open(OUT) as f:
        return json.load(f)


def test_output_exists():
    assert os.path.isfile(OUT), "pauses.json not found"
    assert isinstance(load(), dict)


def test_schema():
    d = load()
    for k in ("audio_duration_seconds", "segments", "total_segments", "total_duration_seconds"):
        assert k in d, f"missing {k}"
    assert isinstance(d["segments"], list)
    for s in d["segments"]:
        for k in ("start", "end", "duration"):
            assert k in s
        assert abs(float(s["end"]) - float(s["start"]) - float(s["duration"])) < 1e-6


def test_audio_duration():
    n, _ = expected()
    assert abs(float(load()["audio_duration_seconds"]) - n) < 1e-6


def test_segments_match():
    _, segs = expected()
    got = [(float(s["start"]), float(s["end"])) for s in load()["segments"]]
    assert len(got) == len(segs), f"expected {len(segs)} segments, got {len(got)}"
    for (gs, ge), (es, ee) in zip(got, segs):
        assert abs(gs - es) < 1e-6 and abs(ge - ee) < 1e-6, f"got {(gs, ge)} expected {(es, ee)}"


def test_totals():
    _, segs = expected()
    d = load()
    assert abs(float(d["total_segments"]) - len(segs)) < 1e-6
    assert abs(float(d["total_duration_seconds"]) - sum(e - s for s, e in segs)) < 1e-6
