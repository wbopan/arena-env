#!/usr/bin/env python3
"""Store the episode traces that arena_env/trace.py sends to an ntfy topic.

    python3 tools/trace_collect.py https://ntfy.sh/<topic> traces/

Keeps a subscription open and appends each decoded record to
traces/<tag or 'untagged'>.jsonl. ntfy keeps messages for 12 hours, so after
a restart the collector resumes from the last message id it saw
(traces/.since) and nothing is lost if it was down for less than that.
"""

import base64
import gzip
import json
import sys
import time
import urllib.request
from pathlib import Path


def main(url: str, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    since_file = out / ".since"
    while True:
        since = since_file.read_text().strip() if since_file.exists() else "12h"
        try:
            with urllib.request.urlopen(f"{url.rstrip('/')}/json?since={since}", timeout=90) as resp:
                for line in resp:
                    msg = json.loads(line)
                    if msg.get("event") != "message":
                        continue
                    try:
                        rec = json.loads(gzip.decompress(base64.b64decode(msg["message"])))
                    except Exception:
                        rec = {"raw": msg.get("message", "")[:500]}
                    rec["_id"], rec["_time"] = msg["id"], msg["time"]
                    with open(out / f"{rec.get('tag') or 'untagged'}.jsonl", "a") as f:
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    since_file.write_text(msg["id"])
        except Exception as exc:  # timeouts and dropped streams: reconnect
            print(time.strftime("%H:%M:%S"), "reconnect:", exc, file=sys.stderr, flush=True)
            time.sleep(5)


if __name__ == "__main__":
    main(sys.argv[1], Path(sys.argv[2]))
