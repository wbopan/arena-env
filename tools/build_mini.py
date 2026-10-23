#!/usr/bin/env python3
"""
Assemble one build context that serves every validated sibling task (check.json ok) from
SIBLINGS. The image is python:3.12-slim plus the common libraries; each task's inputs are
generated at reset by its gen_data.py, so the image stays small.

    build_mini.py SIBLINGS OUT [--runtime arena-runtime:local] [--only a,b]
    docker build --platform linux/amd64 -t arena-mini:local OUT
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_task import PROTOCOL  # noqa: E402
from make_sibling import LIBS  # noqa: E402

TEST_SH = """#!/bin/bash
mkdir -p /logs/verifier
cd /root/work
python3 -m pytest -q -p no:cacheprovider --ctrf /logs/verifier/ctrf.json /verifier/test_outputs.py -rA
if [ $? -eq 0 ]; then echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi
exit 0
"""

DOCKERFILE = """ARG ARENA_RUNTIME={runtime}
FROM ${{ARENA_RUNTIME}} AS arena_runtime
FROM python:3.12-slim
ENV DEBIAN_FRONTEND=noninteractive PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates jq less procps \\
    && rm -rf /var/lib/apt/lists/*
RUN pip install -q {libs} pytest==8.4.1 pytest-json-ctrf==0.3.5
COPY --from=arena_runtime /opt/arena /opt/arena
COPY tasks /opt/arena/tasks
RUN mkdir -p /root/work
ENV ARENA_TRACE_URL={trace_url} ARENA_TRACE_TAG={trace_tag}
WORKDIR /root/work
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=6 CMD curl -fsS http://127.0.0.1:8000/health || exit 1
ENTRYPOINT []
CMD ["/opt/arena/venv/bin/python", "-m", "arena_env.app"]
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("siblings", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--runtime", default="arena-runtime:local")
    ap.add_argument("--only")
    ap.add_argument("--trace-url", default="", help="ntfy topic URL for episode traces (arena_env/trace.py)")
    ap.add_argument("--trace-tag", default="", help="label stored with every trace, e.g. the submission version")
    ap.add_argument("--all", action="store_true", help="include tasks without a passing check.json too")
    args = ap.parse_args()
    if args.out.exists():
        shutil.rmtree(args.out)
    (args.out / "tasks").mkdir(parents=True)
    manifest = []
    for d in sorted(p for p in args.siblings.iterdir() if (p / "task.json").is_file()):
        if args.only and d.name not in args.only.split(","):
            continue
        check = d / "check.json"
        if not args.all and not (check.is_file() and json.loads(check.read_text()).get("ok")):
            continue
        meta = json.loads((d / "task.json").read_text(encoding="utf-8"))
        workdir = meta.get("workdir", "/root/work")
        td = args.out / "tasks" / d.name
        (td / "verifier").mkdir(parents=True)
        shutil.copy(d / "gen_data.py", td / "gen_data.py")
        shutil.copy(d / "verifier" / "test_outputs.py", td / "verifier" / "test_outputs.py")
        (td / "verifier" / "test.sh").write_text(TEST_SH)
        instructions = {"n": meta["instruction"].strip() + PROTOCOL.format(workdir=workdir)}
        hint = d / "hint.md"
        if hint.is_file():
            instructions["h"] = meta["instruction"].strip() + "\n\n## Hint\n\n" + hint.read_text().strip() + PROTOCOL.format(workdir=workdir)
        (td / "task.json").write_text(json.dumps({
            "name": d.name, "workdir": workdir, "category": meta.get("category"), "source": meta.get("source"),
            "instructions": instructions, "default_variant": "n"}, indent=1, ensure_ascii=False) + "\n")
        manifest.append({"task_id": d.name, "category": meta.get("category"), "source": meta.get("source"),
                         "variants": sorted(instructions)})
    (args.out / "Dockerfile").write_text(DOCKERFILE.format(runtime=args.runtime, libs=LIBS,
                                                          trace_url=args.trace_url or '""', trace_tag=args.trace_tag or '""'))
    (args.out / "tasks.jsonl").write_text("".join(json.dumps(m) + "\n" for m in manifest))
    print(f"{len(manifest)} tasks -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
