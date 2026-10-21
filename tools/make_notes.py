#!/usr/bin/env python3
"""
Write reference notes (notes/<task>.md, the s variant) and a short hint
(notes/<task>.hint.md, the h variant) for each task, from its task.md and the
SKILL.md files in environment/skills/. The reference solution is never shown
to the model that writes the notes, so the notes teach the method, not the answer.

    NOTES_API_KEY=... make_notes.py SRC_ROOT NOTES_DIR [--model M] [--base-url U] [--parallel 4] [--only a,b]
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PROMPT = """You are preparing training material for a small terminal agent (a 27B model) that must solve the task below inside a Linux container with at most ~30 shell commands and a tight token budget (it cannot afford to print whole files). The task's author shipped skill documents (SKILL.md) that an expert would read first. Distill them, together with the task statement, into two things.

1. REFERENCE NOTES (at most 1200 words): the procedure and the facts an expert needs to solve THIS task with these tools, in plain prose and short code snippets. Cover: which libraries/commands to use for each input and output format and the exact calls that work; domain formulas, conventions and pitfalls from the skills that apply; a step-by-step plan (inspect inputs cheaply with head/wc/python one-liners, write one script, run it, check the output against the required format, then evaluate); the output file path and format requirements restated precisely. Do not restate the task narrative. Do not guess the answer or the hidden test's values.

2. HINT (3 to 5 lines): the plan in its shortest form (what to inspect, which library, what to write where, then evaluate).

Reply in exactly this layout:
### NOTES
...
### HINT
...

=== TASK (task.md) ===
{task}

=== SKILLS ===
{skills}
"""


def frontmatter_body(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :].lstrip("\n")
    return text


def collect_skills(skills_dir: Path, limit: int = 60000) -> str:
    parts = []
    for md in sorted(skills_dir.rglob("*.md")):
        rel = md.relative_to(skills_dir)
        body = md.read_text(encoding="utf-8", errors="replace")
        parts.append(f"--- {rel} ---\n{body.strip()}")
    for py in sorted(skills_dir.rglob("*.py"))[:12]:
        rel = py.relative_to(skills_dir)
        body = py.read_text(encoding="utf-8", errors="replace")
        parts.append(f"--- {rel} (script, first 60 lines) ---\n" + "\n".join(body.splitlines()[:60]))
    text = "\n\n".join(parts)
    return text[:limit] + ("\n[...]" if len(text) > limit else "")


def ask(base_url: str, key: str, model: str, prompt: str) -> str:
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 9000, "temperature": 0.3}
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def split_reply(text: str) -> tuple[str, str]:
    m = re.search(r"[#*\s]*NOTES[#*:\s]*\n(.*?)\n[#*\s]*HINT[#*:\s]*\n(.*)", text, re.S | re.I)
    if not m:
        raise ValueError("reply not in the expected layout")
    return m.group(1).strip(), m.group(2).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("notes", type=Path)
    ap.add_argument("--model", default="openrouter/anthropic/claude-opus-5.5")
    ap.add_argument("--base-url", default="https://infra.wenbo.io/litellm/v1")
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--only")
    args = ap.parse_args()
    key = os.environ.get("NOTES_API_KEY")
    if not key:
        print("NOTES_API_KEY not set", file=sys.stderr)
        return 2
    args.notes.mkdir(parents=True, exist_ok=True)
    tasks = sorted(d for d in args.src.iterdir() if (d / "task.md").is_file())
    if args.only:
        tasks = [t for t in tasks if t.name in args.only.split(",")]

    def job(d: Path) -> str:
        out = args.notes / f"{d.name}.md"
        if out.exists():
            return f"{d.name}: exists"
        skills_dir = d / "environment" / "skills"
        task = frontmatter_body((d / "task.md").read_text(encoding="utf-8"))
        skills = collect_skills(skills_dir) if skills_dir.is_dir() else "(no skill documents shipped)"
        try:
            reply = ask(args.base_url, key, args.model, PROMPT.format(task=task, skills=skills))
            notes, hint = split_reply(reply)
        except Exception as exc:
            return f"{d.name}: FAILED {exc!r}"
        out.write_text(notes + "\n", encoding="utf-8")
        (args.notes / f"{d.name}.hint.md").write_text(hint + "\n", encoding="utf-8")
        return f"{d.name}: {len(notes.split())} words, hint {len(hint.splitlines())} lines"

    with ThreadPoolExecutor(args.parallel) as ex:
        for line in ex.map(job, tasks):
            print(line, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
