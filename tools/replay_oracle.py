#!/usr/bin/env python3
"""
Play a task's reference solution through a running server and print the reward.

    replay_oracle.py --url http://localhost:8000 --task-id NAME--n ORACLE_DIR

The oracle directory's files are written into /oracle in the sandbox through
write_file, then solve.sh runs through exec, then evaluate is called.
"""

import argparse
import json
import sys
from pathlib import Path

from wsclient import Session


def step(sess: Session, action: dict) -> dict:
    res = sess.step(action)
    res["observation"].update(reward=res.get("reward"), done=res.get("done"))
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("oracle", type=Path)
    ap.add_argument("--url", default="http://localhost:8000")
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--chunk", type=int, default=200000)
    args = ap.parse_args()

    sess = Session(args.url, timeout=600)
    obs = sess.reset(task_id=args.task_id)["observation"]
    print(f"reset ok; instruction {len(obs.get('instruction', ''))} chars, variant {obs.get('task_id')}")

    for f in sorted(args.oracle.rglob("*")):
        if f.is_file():
            content = f.read_text(encoding="utf-8", errors="replace")
            res = step(sess, {"action_type": "write_file",
                                  "file_path": f"/oracle/{f.relative_to(args.oracle)}",
                                  "content": content})
            if not res["observation"].get("success", True):
                print("write failed:", res["observation"].get("error"))
    res = step(sess, {"action_type": "exec", "command": f"cd {obs.get('task_path', '/root')} && bash /oracle/solve.sh 2>&1 | tail -20"})
    obs = res["observation"]
    print("solve.sh output:\n" + obs.get("output", "")[-1500:])
    res = step(sess, {"action_type": "evaluate"})
    obs = res["observation"]
    print(json.dumps({"reward": obs.get("reward"), "done": obs.get("done"),
                      "output": obs.get("output")}, indent=1))
    sess.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
