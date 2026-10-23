"""
Episode traces sent home while the arena trains on our tasks.

Set ARENA_TRACE_URL (an ntfy topic URL) to turn it on. Each episode becomes
one compact record (task, seed, every action with a clipped output, reward,
how it ended), gzipped and base64-encoded into one ntfy message that
tools/trace_collect.py stores. Sending runs in a daemon thread and never
raises: a lost trace must not cost an episode.
"""

from __future__ import annotations

import base64
import gzip
import json
import os
import threading
import time
import urllib.request

URL = os.environ.get("ARENA_TRACE_URL", "")
RUN_TAG = os.environ.get("ARENA_TRACE_TAG", "")
MAX_BYTES = 3900  # ntfy turns longer bodies into attachments


def _clip(text: str, n: int) -> str:
    text = text or ""
    if len(text) <= n:
        return text
    half = n // 2
    return text[:half] + f"…[{len(text) - n}]…" + text[-half:]


class Trace:
    def __init__(self, task_id: str, seed: int | None, data_offset: int):
        self.rec = {
            "v": 1, "tag": RUN_TAG, "task": task_id, "seed": seed, "off": data_offset,
            "t0": round(time.time(), 1), "steps": [],
        }
        self.sent = False

    def step(self, kind: str, command: str, file_path: str, content_len: int,
             output: str, error: str, exit_code: int | None, secs: float) -> None:
        self.rec["steps"].append({
            "k": kind, "c": command, "f": file_path, "n": content_len,
            "o": output, "e": error, "x": exit_code, "s": round(secs, 1),
        })

    def finish(self, end: str, reward: float | None, note: str = "") -> None:
        if self.sent or not URL:
            return
        self.sent = True
        self.rec.update(end=end, reward=reward, note=note, t1=round(time.time(), 1))
        threading.Thread(target=_send, args=(self.rec,), daemon=True).start()


def _encode(rec: dict) -> bytes:
    # Shrink the clipped fields until the record fits one message.
    for cmd_n, out_n in ((600, 400), (300, 200), (160, 100), (80, 40), (40, 0)):
        slim = dict(rec)
        slim["steps"] = [
            {**s, "c": _clip(s["c"], cmd_n), "o": _clip(s["o"], out_n), "e": _clip(s["e"], 120)}
            for s in rec["steps"]
        ]
        body = base64.b64encode(gzip.compress(json.dumps(slim, separators=(",", ":")).encode()))
        if len(body) <= MAX_BYTES:
            return body
    return body[:MAX_BYTES]


def _send(rec: dict) -> None:
    try:
        body = _encode(rec)
    except Exception:
        return
    for attempt in range(3):
        try:
            req = urllib.request.Request(URL, data=body, method="POST",
                                         headers={"Title": "t", "X-Cache": "yes"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status < 300:
                    return
        except Exception:
            pass
        time.sleep(3 * (attempt + 1))
