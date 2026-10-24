#!/usr/bin/env python3
"""Write siblings/<task>/skill.md: reference notes distilled from the parent SkillsBench task's skills.

    LLM_BASE_URL=... LLM_MODEL=... LLM_API_KEY=... gen_skill.py SIBLINGS SKILLSBENCH_DIR [--only a,b] [--force] [-j 6]

SKILLSBENCH_DIR holds the public SkillsBench tasks (<task>/environment/skills/). The model is called
through an OpenAI-compatible /responses endpoint. build_mini.py turns skill.md into the "s" variant.
"""
import argparse
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MAX_SKILL_CHARS = 60000
MAX_NOTE_CHARS = 5000

PROMPT = """You write the "Reference notes" section that is appended to a terminal task for a small (27B) coding agent.
The agent has a 4096-token completion budget for the whole episode (every command it writes and every output it reads counts), so it must inspect files cheaply, write one script, run it, check the output and evaluate.

Below are (1) the task the agent will get and (2) the skill documents that came with a related task. Distill from the skill documents only the knowledge this task needs: which installed Python library or CLI to use, the exact API calls and their argument conventions, file-format pitfalls, domain formulas and definitions, and a short workflow. Prefer a compact code skeleton the agent can adapt over prose.

Rules:
- At most {max_chars} characters. Markdown, terse, no preamble.
- Do not solve the task: no computed values, no task-specific answers, no complete solution script. Generic snippets (open the file, read the table, write the output) are fine.
- Do not mention tests, verifiers, graders or how the task is scored.
- Do not invent facts that are neither in the skill documents nor standard library documentation. If the skill documents do not apply to this task, write general advice for the file formats and computations the task involves.
- Only use libraries that are plausibly installed: Python standard library, numpy, pandas, openpyxl, pypdf, python-docx, python-pptx, scipy, and whatever the task text names.

# Task
{task}

# Skill documents
{skills}
"""


def skills_text(skills_dir: Path) -> str:
    parts = []
    for f in sorted(skills_dir.rglob("*.md")):
        if f.name.upper().startswith("LICENSE"):
            continue
        txt = f.read_text(encoding="utf-8", errors="replace")
        parts.append(f"## {f.relative_to(skills_dir)}\n\n{txt}")
    out = "\n\n".join(parts)
    return out[:MAX_SKILL_CHARS]


def call(prompt: str, key: str) -> str:
    body = json.dumps({"model": os.environ["LLM_MODEL"], "input": prompt}).encode()
    req = urllib.request.Request(f"{os.environ['LLM_BASE_URL'].rstrip('/')}/responses", data=body, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.load(r)
    texts = [c["text"] for o in d.get("output", []) if o.get("type") == "message"
             for c in o.get("content", []) if c.get("type") == "output_text"]
    return "\n".join(texts).strip()


def one(d: Path, sb: Path, key: str, force: bool) -> str:
    out = d / "skill.md"
    if out.exists() and not force:
        return f"skip {d.name}"
    meta = json.loads((d / "task.json").read_text(encoding="utf-8"))
    skills_dir = sb / meta["source"] / "environment" / "skills"
    skills = skills_text(skills_dir) if skills_dir.is_dir() else "(none)"
    prompt = PROMPT.format(max_chars=MAX_NOTE_CHARS, task=meta["instruction"].strip(), skills=skills)
    for attempt in range(3):
        try:
            note = call(prompt, key)
        except Exception as exc:  # gateway hiccups
            note, err = "", exc
            continue
        if note and len(note) <= MAX_NOTE_CHARS * 1.2:
            out.write_text(note + "\n", encoding="utf-8")
            return f"ok {d.name} {len(note)}"
        prompt += f"\n\nYour previous answer was {len(note)} characters; stay under {MAX_NOTE_CHARS}."
    return f"FAIL {d.name}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("siblings", type=Path)
    ap.add_argument("skillsbench", type=Path)
    ap.add_argument("--only")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("-j", type=int, default=6)
    a = ap.parse_args()
    key = os.environ["LLM_API_KEY"]
    dirs = []
    for d in sorted(p for p in a.siblings.iterdir() if (p / "task.json").is_file()):
        if a.only and d.name not in a.only.split(","):
            continue
        check = d / "check.json"
        if check.is_file() and json.loads(check.read_text()).get("ok"):
            dirs.append(d)
    with ThreadPoolExecutor(a.j) as ex:
        for msg in ex.map(lambda d: one(d, a.skillsbench, key, a.force), dirs):
            print(msg, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
