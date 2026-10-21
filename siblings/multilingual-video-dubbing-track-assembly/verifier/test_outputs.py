import json
import os
import wave

import numpy as np
import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "dubbed_track.wav")


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
        cues[int(lines[0].strip())] = (to_sec(a), to_sec(b))
    return cues


def read_wav(path):
    with wave.open(path, "rb") as w:
        params = (w.getnchannels(), w.getsampwidth(), w.getframerate())
        data = w.readframes(w.getnframes())
    return params, np.frombuffer(data, dtype="<i2").astype(np.float64)


def expected():
    with open(os.path.join(WORK, "timeline.json")) as f:
        tl = json.load(f)
    sr = int(tl["sample_rate"])
    L = int(round(tl["duration_sec"] * sr))
    out = np.zeros(L)
    regions = []
    for k, (s0, e0) in sorted(read_srt(os.path.join(WORK, "segments.srt")).items()):
        _, a = read_wav(os.path.join(WORK, "tts", "seg_%d.wav" % k))
        rms = np.sqrt(np.mean((a / 32768.0) ** 2))
        a = a * (0.1 / rms)
        s = int(round(s0 * sr))
        e = int(round(e0 * sr))
        a = a[: e - s]
        out[s:s + len(a)] = a
        regions.append((s, s + len(a)))
    out = np.clip(np.round(out), -32768, 32767)
    return sr, L, out, regions


def test_exists_and_format():
    assert os.path.exists(OUT), "dubbed_track.wav missing"
    params, _ = read_wav(OUT)
    assert params == (1, 2, 16000), f"bad format {params}"


def test_length():
    sr, L, _, _ = expected()
    _, y = read_wav(OUT)
    assert len(y) == L, f"{len(y)} frames != {L}"


def test_silence_outside_clips():
    _, L, _, regions = expected()
    _, y = read_wav(OUT)
    assert len(y) == L
    mask = np.ones(L, dtype=bool)
    for s, e in regions:
        mask[s:e] = False
    assert np.max(np.abs(y[mask])) <= 1, "non-silent samples outside placed clips"


def test_clip_loudness():
    _, L, exp, regions = expected()
    _, y = read_wav(OUT)
    assert len(y) == L
    for s, e in regions:
        r_got = np.sqrt(np.mean((y[s:e] / 32768.0) ** 2)) + 1e-12
        r_exp = np.sqrt(np.mean((exp[s:e] / 32768.0) ** 2)) + 1e-12
        assert abs(20 * np.log10(r_got / r_exp)) <= 0.2, f"clip at {s} loudness off"


def test_samples_match():
    _, L, exp, _ = expected()
    _, y = read_wav(OUT)
    assert len(y) == L
    diff = np.max(np.abs(y - exp))
    assert diff <= 1, f"max sample difference {diff}"
