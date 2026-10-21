#!/usr/bin/env python3
"""
Turn one task directory (task.md, environment/, verifier/, oracle/) into a
Docker build context that serves it as an OpenEnv environment.

    build_task.py SRC OUT [--digest FILE] [--hint FILE] [--runtime IMAGE]

OUT/Dockerfile is the task's own Dockerfile with the server layer appended,
so the task image is built exactly as its author wrote it. Build with:

    docker build --platform linux/amd64 -t <image> OUT
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

import yaml

PROTOCOL = (
    "\n\n---\n"
    "You work as root in {workdir} through a terminal. Actions: exec (run a shell "
    "command), write_file (file_path, content), evaluate (grades your work and ends "
    "the episode; call it once you are done). Keep outputs short: inspect files with "
    "head, wc, grep or small scripts instead of printing them whole.\n"
    "Reply with exactly one JSON object and nothing else. Inside the command string "
    "quote with single quotes and escape every double quote and newline (\\\" and \\n); "
    "create or overwrite files with write_file, never with heredocs."
)
DIGEST_MAX_CHARS = 12000


def split_frontmatter(text: str) -> tuple[dict, str]:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            meta = yaml.safe_load(text[3:end]) or {}
            return meta, text[end + 4 :].lstrip("\n")
    return {}, text


def workdir_of(dockerfile: str) -> str:
    wd = "/root"
    for line in dockerfile.splitlines():
        m = re.match(r"\s*WORKDIR\s+(\S+)", line)
        if m and not m.group(1).startswith("$"):
            wd = m.group(1)
    return wd


def auto_digest(skills_dir: Path) -> str:
    """Fallback reference notes: the task's SKILL.md files, trimmed."""
    parts = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        meta, body = split_frontmatter(skill_md.read_text(encoding="utf-8", errors="replace"))
        name = meta.get("name") or skill_md.parent.name
        parts.append(f"### {name}\n{body.strip()}")
    text = "\n\n".join(parts)
    if len(text) > DIGEST_MAX_CHARS:
        text = text[:DIGEST_MAX_CHARS] + "\n[...]"
    return text


def patch_test_sh(text: str) -> str:
    """Skip the uv installer when uv is already there (the image preinstalls it)."""
    return re.sub(
        r"^(\s*)(curl -LsSf https://astral\.sh/uv/[^\n|]*install\.sh\s*\|\s*sh\b[^\n]*)$",
        r"\1command -v uv >/dev/null 2>&1 || \2",
        text,
        flags=re.M,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--digest", type=Path, help="reference notes for the s variant")
    ap.add_argument("--hint", type=Path, help="short hint for the h variant")
    ap.add_argument("--runtime", default="arena-runtime:local", help="runtime image to copy /opt/arena from")
    ap.add_argument("--name", help="task name (default: source directory name)")
    args = ap.parse_args()

    src: Path = args.src
    out: Path = args.out
    name = args.name or src.name
    env_dir = src / "environment"
    if not (env_dir / "Dockerfile").is_file():
        print(f"{src}: no environment/Dockerfile", file=sys.stderr)
        return 2

    meta, body = split_frontmatter((src / "task.md").read_text(encoding="utf-8"))
    dockerfile = (env_dir / "Dockerfile").read_text(encoding="utf-8")
    workdir = workdir_of(dockerfile)
    footer = PROTOCOL.format(workdir=workdir)
    body = body.strip()

    instructions = {"n": body + footer}
    skills_dir = env_dir / "skills"
    digest = args.digest.read_text(encoding="utf-8").strip() if args.digest else (
        auto_digest(skills_dir) if skills_dir.is_dir() else ""
    )
    if digest:
        instructions["s"] = body + "\n\n## Reference notes\n\n" + digest + footer
    if args.hint:
        instructions["h"] = body + "\n\n## Hint\n\n" + args.hint.read_text(encoding="utf-8").strip() + footer

    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(env_dir, out, symlinks=True)
    arena = out / "arena"
    arena.mkdir()
    shutil.copytree(src / "verifier", arena / "verifier")
    test_sh = arena / "verifier" / "test.sh"
    if test_sh.is_file():
        test_sh.write_text(patch_test_sh(test_sh.read_text(encoding="utf-8")), encoding="utf-8")
    (arena / "task.json").write_text(
        json.dumps(
            {
                "name": name,
                "workdir": workdir,
                "category": (meta.get("metadata") or {}).get("category"),
                "difficulty": (meta.get("metadata") or {}).get("difficulty"),
                "verifier_timeout_s": (meta.get("verifier") or {}).get("timeout_sec"),
                "default_variant": "n",
                "instructions": instructions,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )

    head = f"ARG ARENA_RUNTIME={args.runtime}\nFROM ${{ARENA_RUNTIME}} AS arena_runtime\n\n"
    tail = f"""

# ---------------- arena-env server layer ----------------
USER root
ENV DEBIAN_FRONTEND=noninteractive UV_CACHE_DIR=/opt/arena/uv-cache
COPY --from=arena_runtime /opt/arena /opt/arena
COPY arena /opt/arena/task
RUN /opt/arena/venv/bin/python /opt/arena/pkg/prepare_image.py
WORKDIR {workdir}
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \\
  CMD /opt/arena/venv/bin/python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" || exit 1
ENTRYPOINT []
CMD ["/opt/arena/venv/bin/python", "-m", "arena_env.app"]
"""
    (out / "Dockerfile").write_text(head + dockerfile.rstrip("\n") + tail, encoding="utf-8")
    print(f"{name}: context at {out} (workdir {workdir}, variants {sorted(instructions)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
