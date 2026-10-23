#!/usr/bin/env python3
"""
Validate sibling tasks locally: for each OUT/<name>, in a fresh /root/work run gen_data.py,
grade (expect reward 0), run the oracle, grade again (expect 1). Writes OUT/<name>/check.json.

    check_sibling.py OUT [--only a,b] [--python /path/to/venv/bin/python]
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arena_env.seeded import RUNNER  # noqa: E402

WORK = Path("/root/work")


def run(cmd, cwd, timeout=300, env=None):
    try:
        p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=timeout, env=env)
        return p.returncode, (p.stdout + p.stderr)[-3000:]
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def fresh_work():
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)


def grade(py, task_dir, env):
    code, out = run([py, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(task_dir / "verifier" / "test_outputs.py")], WORK, env=env)
    return int(code == 0), out


def check(py, task_dir: Path, seed: int = 0) -> dict:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    res = {"name": task_dir.name, "ok": False}
    fresh_work()
    code, out = run([py, "-c", RUNNER, str(task_dir / "gen_data.py"), str(seed)], WORK, env=env)
    res["gen"] = code
    if code != 0:
        res["gen_out"] = out
        return res
    files = sorted(p for p in WORK.rglob("*") if p.is_file())
    res["inputs"] = {str(p.relative_to(WORK)): p.stat().st_size for p in files}
    res["blank_reward"], blank_out = grade(py, task_dir, env)
    code, out = run(["bash", str(task_dir / "oracle" / "solve.sh")], WORK, env=env)
    res["oracle_exit"] = code
    if code != 0:
        res["oracle_out"] = out
    res["oracle_reward"], oracle_out = grade(py, task_dir, env)
    if res["oracle_reward"] != 1:
        res["oracle_grade_out"] = oracle_out
    res["ok"] = res["gen"] == 0 and res["blank_reward"] == 0 and res["oracle_exit"] == 0 and res["oracle_reward"] == 1
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--only")
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--seeds", default="0", help="comma-separated seed offsets; a task is ok only if all pass")
    ap.add_argument("--out-name", default="check.json")
    args = ap.parse_args()
    args.out = args.out.resolve()
    dirs = sorted(d for d in args.out.iterdir() if (d / "task.json").is_file())
    if args.only:
        dirs = [d for d in dirs if d.name in args.only.split(",")]
    n_ok = 0
    for d in dirs:
        runs = [check(args.python, d, int(s)) for s in args.seeds.split(",")]
        res = dict(runs[0], ok=all(r["ok"] for r in runs), seeds={s: r["ok"] for s, r in zip(args.seeds.split(","), runs)})
        bad = [r for r in runs if not r["ok"]]
        if bad:
            res.update({k: v for k, v in bad[0].items() if k not in ("ok",)})
        (d / args.out_name).write_text(json.dumps(res, indent=1) + "\n")
        n_ok += res["ok"]
        print(f"{d.name:60s} {'OK' if res['ok'] else 'FAIL'} seeds={res.get('seeds')} gen={res['gen']} blank={res.get('blank_reward')} oracle={res.get('oracle_exit')}/{res.get('oracle_reward')}", flush=True)
    print(f"{n_ok}/{len(dirs)} ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
