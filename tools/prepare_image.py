"""
Runs once inside a task image at build time, after the task's own Dockerfile:

1. puts uv where test.sh scripts expect it, and pytest into the task's python;
2. snapshots the working directory, so reset() can restore it;
3. runs the verifier once against the untouched workdir to warm its caches
   (uvx tools, pip wheels), then restores the workdir from the snapshot.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tarfile
from pathlib import Path

ARENA = Path("/opt/arena")
TASK = ARENA / "task"
UV = ARENA / "bin" / "uv"


def sh(cmd: str, timeout: float) -> int:
    try:
        return subprocess.run(["/bin/bash", "-c", cmd], timeout=timeout).returncode
    except subprocess.TimeoutExpired:
        print(f"[prepare] timed out: {cmd[:80]}")
        return 124


def snapshot(workdir: Path) -> None:
    with tarfile.open(TASK / "snapshot.tar", "w") as tar:
        tar.add(workdir, arcname=str(workdir.relative_to("/")))


def restore(workdir: Path) -> None:
    for child in workdir.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child, ignore_errors=True)
        else:
            child.unlink(missing_ok=True)
    with tarfile.open(TASK / "snapshot.tar") as tar:
        tar.extractall("/", numeric_owner=True)


def main() -> None:
    meta = json.loads((TASK / "task.json").read_text())
    workdir = Path(meta["workdir"])
    workdir.mkdir(parents=True, exist_ok=True)

    for dest in (Path("/root/.local/bin/uv"), Path("/usr/local/bin/uv")):
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(UV, dest)
    if shutil.which("pip3") or shutil.which("pip"):
        sh("(pip3 --version >/dev/null 2>&1 && pip3 install -q --break-system-packages "
           "pytest==8.4.1 pytest-json-ctrf==0.3.5) || pip install -q pytest==8.4.1 pytest-json-ctrf==0.3.5",
           600)

    snapshot(workdir)

    verifier = TASK / "verifier"
    if (verifier / "test.sh").is_file():
        stage = Path("/verifier")
        shutil.rmtree(stage, ignore_errors=True)
        shutil.copytree(verifier, stage)
        Path("/logs/verifier").mkdir(parents=True, exist_ok=True)
        code = sh(f"cd {workdir} && bash /verifier/test.sh", 900)
        reward = Path("/logs/verifier/reward.txt")
        print(f"[prepare] warm-up verifier exit {code}, reward.txt: "
              f"{reward.read_text().strip() if reward.is_file() else 'missing'}")
        shutil.rmtree(stage, ignore_errors=True)
        shutil.rmtree("/logs/verifier", ignore_errors=True)
        restore(workdir)

    (ARENA / "uv-cache").mkdir(exist_ok=True)
    print(f"[prepare] done: workdir {workdir}, snapshot {os.path.getsize(TASK / 'snapshot.tar')} bytes")


if __name__ == "__main__":
    main()
