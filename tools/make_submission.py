#!/usr/bin/env python3
"""
Pick tasks by screening solve rate and write the arena submission JSON.

    make_submission.py --id arena-env-v1 --schema schema.json --mini-summary cal/mini1/summary.json \
        --mini-image ghcr.io/wbopan/arena-env/mini:v1 [--orig-dir cal/pass5 --orig-image-prefix ghcr.io/wbopan/arena-env/] \
        [--min 0.25 --max 0.75 --limit 50] -o submission.json

Mini tasks keep the arena's default budgets (they were screened at 4096/8192). Original tasks
get the maximum budgets, their own image and a longer rollout wall.
"""

import argparse
import json
from pathlib import Path


def pick(summary: Path, lo: float, hi: float) -> list[tuple[str, float]]:
    s = json.loads(summary.read_text())
    out = []
    for tid, r in s["tasks"].items():
        rate = r["solved"] / r["n"] if r["n"] else 0.0
        if lo <= rate <= hi:
            out.append((tid, rate))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--name", default="Compact terminal tasks")
    ap.add_argument("--schema", type=Path, required=True)
    ap.add_argument("--mini-summary", type=Path)
    ap.add_argument("--mini-image", default="ghcr.io/wbopan/arena-env/mini:v1")
    ap.add_argument("--orig-dir", type=Path, help="cal/<run> with <task>/summary.json per original task")
    ap.add_argument("--orig-image-prefix", default="ghcr.io/wbopan/arena-env/")
    ap.add_argument("--orig-tag", default="v1")
    ap.add_argument("--min", type=float, default=0.25)
    ap.add_argument("--max", type=float, default=0.75)
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--dataset", default="wenbopan/arena-env")
    ap.add_argument("--source", default="https://github.com/wbopan/arena-env")
    ap.add_argument("-o", "--out", type=Path, default=Path("submission.json"))
    args = ap.parse_args()

    schema = json.loads(args.schema.read_text())
    tasks = []
    if args.mini_summary:
        for tid, rate in sorted(pick(args.mini_summary, args.min, args.max), key=lambda x: (-x[1], x[0])):
            tasks.append({"task_id": tid, "split": "train", "_rate": rate})
    if args.orig_dir:
        for d in sorted(args.orig_dir.iterdir()):
            s = d / "summary.json"
            if not s.is_file():
                continue
            for tid, rate in pick(s, args.min, args.max):
                name = tid.split("--")[0]
                tasks.append({"task_id": tid, "split": "train", "image": f"{args.orig_image_prefix}{name}:{args.orig_tag}",
                              "completion_tokens": 32768, "context_tokens": 32768, "tool_calls_total": 128,
                              "reset_wall_s": 180, "rollout_wall_s": 3000, "verifier_wall_s": 300, "_rate": rate})
    # keep the middle of the band first, then fill up to the limit
    tasks.sort(key=lambda t: abs(t["_rate"] - 0.5))
    tasks = tasks[: args.limit]
    tasks.sort(key=lambda t: t["task_id"])
    rates = {t["task_id"]: t.pop("_rate") for t in tasks}
    sub = {
        "submission_id": args.id,
        "name": args.name,
        "image": args.mini_image,
        "schema": {"action": schema["action"], "observation": schema["observation"]},
        "tasks": tasks,
        "example_actions": [{"action_type": "exec", "command": "ls"}, {"action_type": "evaluate"}],
        "finish_action": {"action_type": "evaluate"},
        "dataset": args.dataset,
        "source": args.source,
    }
    args.out.write_text(json.dumps(sub, indent=1) + "\n")
    images = {t.get("image", args.mini_image) for t in tasks}
    print(f"{len(tasks)} tasks, {len(images)} images -> {args.out}")
    for t in tasks:
        print(f"  {t['task_id']:60s} {rates[t['task_id']]:.2f}")
    return 0


if __name__ == "__main__":
    main()
