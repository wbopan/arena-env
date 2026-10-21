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


GHCR = "ghcr.io/wbopan/arena-env"


def variants(task: str, image: str | None = None) -> list[str]:
    p = ROOT / "build" / task / "arena" / "task.json"
    if image is None and p.exists():
        meta = json.loads(p.read_text())
    else:  # pulled image: read the task.json baked into it
        out = subprocess.run(["docker", "run", "--rm", "--entrypoint", "cat", image, "/opt/arena/task/task.json"],
                             text=True, capture_output=True, check=True).stdout
        meta = json.loads(out)
    return [f"{task}--{v}" for v in meta["instructions"]]


MAX_PULL_GB = 2.5  # compressed size; bigger images are left for a host with disk to spare


def ghcr_pull(task: str, tag: str) -> bool:
    """Pull the task image from GHCR and tag it arena-task/<task>:local. False if it is not published yet or too big."""
    ref = f"{GHCR}/{task}:{tag}"
    m = subprocess.run(["docker", "manifest", "inspect", ref], text=True, capture_output=True)
    if m.returncode != 0:
        return False
    size = sum(l["size"] for l in json.loads(m.stdout).get("layers", [])) / 1e9
    if size > MAX_PULL_GB:
        print(f"  skip {task}: {size:.1f} GB compressed", flush=True)
        (ROOT / "cal" / "skipped_big.txt").open("a").write(f"{task}\t{size:.1f}\n")
        return False
    if subprocess.run(["docker", "pull", "-q", ref], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        return False
    subprocess.run(["docker", "tag", ref, f"arena-task/{task}:local"], check=True)
    subprocess.run(["docker", "rmi", ref], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True


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
    ap.add_argument("--variants", help="comma-separated variant letters to play (default: all in the image)")
    ap.add_argument("--rm-image", action="store_true", help="remove the task image after screening it (disk)")
    ap.add_argument("--ghcr", metavar="TAG", help="pull images ghcr.io/wbopan/arena-env/<task>:TAG for the tasks in tasks.txt instead of using local builds")
    ap.add_argument("rest", nargs=argparse.REMAINDER, help="extra calibrate.py args")
    args = ap.parse_args()
    args.rest = [a for a in args.rest if a != "--"]
    out_root = ROOT / "cal" / args.run
    out_root.mkdir(parents=True, exist_ok=True)
    rounds_without_progress = 0
    while True:
        if args.ghcr:
            tasks = [l.strip() for l in (HERE.parent / "tasks.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
            done = True
        else:
            tasks, done = built_tasks()
        if args.only:
            tasks = [t for t in tasks if t in args.only.split(",")]
        skipped = set()
        if (ROOT / "cal" / "skipped_big.txt").exists():
            skipped = {l.split("\t")[0] for l in (ROOT / "cal" / "skipped_big.txt").read_text().splitlines()}
        todo = [t for t in tasks if not (out_root / t / "summary.json").exists() and t not in skipped and (args.ghcr or image_exists(t))]
        progressed = False
        for task in todo:
            if args.ghcr:
                if not image_exists(task) and not ghcr_pull(task, args.ghcr):
                    continue  # not published yet; retried on the next pass
            elif not image_exists(task):
                continue  # rebuilt or removed meanwhile; picked up on the next pass
            progressed = True
            ids = variants(task, f"arena-task/{task}:local" if args.ghcr else None)
            if args.variants:
                ids = [i for i in ids if i.rsplit("--", 1)[1] in args.variants.split(",")]
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
        if args.ghcr:
            rounds_without_progress = 0 if progressed else rounds_without_progress + 1
            if not todo or rounds_without_progress >= 30:  # ~1h with nothing new published
                break
            if not progressed:
                time.sleep(120)
            continue
        if done and not todo:
            break
        if not todo:
            time.sleep(120)
    print("SCREEN_DONE", flush=True)


if __name__ == "__main__":
    main()
