#!/usr/bin/env python3
"""
Assemble the public dataset folder for Hugging Face: README card, tasks.jsonl, and each task's
sources (task.md, gen_data.py, verifier, oracle).

    make_dataset.py SIBLINGS OUT [--submission submission.json]
"""

import argparse
import json
import shutil
from pathlib import Path

README = """---
license: apache-2.0
task_categories: [other]
pretty_name: arena-env
---

# arena-env

Compact terminal tasks for training small coding agents, spread over eight domains
(software engineering, industrial and physical systems, natural science, office work,
finance and economics, mathematics and formal reasoning, cybersecurity, media production).

Each task gives the agent a few generated input files in `/root/work`, a precise
specification of one output file, and a terminal (`exec`, `write_file`, `evaluate`
actions over the Terminal-Bench 2 action schema). The reward is 1 when the task's
pytest verifier passes against the produced output and 0 otherwise; there is no partial credit.
Inputs are regenerated deterministically at every reset by `gen_data.py`.

`tasks.jsonl` lists the tasks (`task_id`, `category`, `source`); each task's folder holds
`task.md`, `gen_data.py`, `verifier/test_outputs.py` and a reference `oracle/solve.sh`.
The tasks were derived from the public SkillsBench tasks (benchflow/skillsbench) as
smaller siblings exercising the same skills.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("siblings", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--submission", type=Path, help="only the tasks of this submission")
    args = ap.parse_args()
    keep = None
    if args.submission:
        keep = {t["task_id"].split("--")[0] for t in json.loads(args.submission.read_text())["tasks"]}
    if args.out.exists():
        shutil.rmtree(args.out)
    args.out.mkdir(parents=True)
    rows = []
    for d in sorted(p for p in args.siblings.iterdir() if (p / "task.json").is_file()):
        if keep is not None and d.name not in keep:
            continue
        check = d / "check.json"
        if not (check.is_file() and json.loads(check.read_text()).get("ok")):
            continue
        meta = json.loads((d / "task.json").read_text())
        td = args.out / "tasks" / d.name
        td.mkdir(parents=True)
        for rel in ("task.md", "gen_data.py", "requirements.txt"):
            if (d / rel).is_file():
                shutil.copy(d / rel, td / rel)
        shutil.copytree(d / "verifier", td / "verifier")
        shutil.copytree(d / "oracle", td / "oracle")
        rows.append({"task_id": f"{d.name}--n", "category": meta.get("category"), "source": meta.get("source"),
                     "workdir": meta.get("workdir", "/root/work")})
    (args.out / "tasks.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    (args.out / "README.md").write_text(README)
    print(f"{len(rows)} tasks -> {args.out}")
    return 0


if __name__ == "__main__":
    main()
