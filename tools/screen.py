#!/usr/bin/env python3
"""
Screen built task images as they appear: for every task marked ok in
build/summary.tsv that has no result yet, play --episodes episodes of each
variant and write cal/<run>/<task>/{episodes.jsonl,summary.json}.
Keeps polling until build/summary.tsv ends with ALL_DONE and all are screened.

    screen.py --run pass1 --episodes 4 --parallel 4 [calibrate.py args...]
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path.home() / "arena"


def variants(task: str) -> list[str]:
    meta = json.loads((ROOT / "build" / task / "arena" / "task.json").read_text())
    return [f"{task}--{v}" for v in meta["instructions"]]


def image_exists(task: str) -> bool:
    return subprocess.run(["docker", "image", "inspect", f"arena-task/{task}:local"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def built_tasks() -> tuple[list[str], bool]:
    tasks, done = [], False
    p = ROOT / "build" / "summary.tsv"
    if not p.exists():
        return tasks, done
    for line in p.read_text().splitlines():
        cols = line.split("\t")
        if cols[0] == "ALL_DONE":
            done = True
        elif len(cols) > 1 and cols[1] in ("ok", "cached"):
            tasks.append(cols[0])
    return tasks, done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--episodes", type=int, default=4)
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--only", help="comma-separated task names")
    ap.add_argument("--rm-image", action="store_true", help="remove the task image after screening it (disk)")
    ap.add_argument("rest", nargs=argparse.REMAINDER, help="extra calibrate.py args")
    args = ap.parse_args()
    args.rest = [a for a in args.rest if a != "--"]
    out_root = ROOT / "cal" / args.run
    out_root.mkdir(parents=True, exist_ok=True)
    while True:
        tasks, done = built_tasks()
        if args.only:
            tasks = [t for t in tasks if t in args.only.split(",")]
        todo = [t for t in tasks if not (out_root / t / "summary.json").exists() and image_exists(t)]
        for task in todo:
            if not image_exists(task):
                continue  # rebuilt or removed meanwhile; picked up on the next pass
            ids = variants(task)
            cmd = [sys.executable, str(HERE / "calibrate.py"), "--tasks", ",".join(ids),
                   "--episodes", str(args.episodes), "--parallel", str(args.parallel),
                   "--tokenizer", str(ROOT / "tokenizer.json"), "--out", str(out_root / task)] + args.rest
            print(time.strftime("%H:%M:%S"), "screening", task, flush=True)
            with open(out_root / f"{task}.log", "w") as log:
                subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
            s = out_root / task / "summary.json"
            if s.exists() and not json.loads(s.read_text())["tasks"]:
                s.unlink()  # every episode failed on infrastructure: screen it again later
            if s.exists():
                for tid, r in json.loads(s.read_text())["tasks"].items():
                    print(f"  {tid:44s} {r['solved']}/{r['n']} ends={r['ends']}", flush=True)
            else:
                print("  no summary (see log)", flush=True)
            if args.rm_image and s.exists():
                subprocess.run(["docker", "rmi", f"arena-task/{task}:local"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if done and not todo:
            break
        if not todo:
            time.sleep(120)
    print("SCREEN_DONE", flush=True)


if __name__ == "__main__":
    main()
