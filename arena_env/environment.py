"""
One task per image, behind the tbench2_env interface.

The image is a task's own environment image with this server layered on top
(see tools/build_task.py). The agent works as root in the task's working
directory, exactly as the task's author intended. ``reset`` restores that
directory from a snapshot taken at build time, so every episode starts from
the same files. ``evaluate`` stages the verifier (held only in the server's
memory) to /verifier, runs test.sh and reads /logs/verifier/reward.txt.

task_id is ``<task>`` or ``<task>--<variant>``; the variant selects which
instruction text the episode shows (see task.json "instructions").
"""

from __future__ import annotations

import io
import json
import os
import shutil
import signal
import subprocess
import tarfile
import threading
import time
from pathlib import Path
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment

from .models import Tbench2Action, Tbench2Observation, Tbench2State

ARENA_DIR = Path(os.environ.get("ARENA_DIR", "/opt/arena"))
TASK_DIR = ARENA_DIR / "task"
VERIFIER_STAGE = Path("/verifier")
LOGS_DIR = Path("/logs/verifier")

MAX_ACTIONS = int(os.environ.get("ARENA_MAX_ACTIONS", "32"))
EXEC_TIMEOUT_S = float(os.environ.get("ARENA_EXEC_TIMEOUT_S", "90"))
EVAL_TIMEOUT_S = float(os.environ.get("ARENA_EVAL_TIMEOUT_S", "100"))
HEAD_CHARS = 3000
TAIL_CHARS = 1000
SESSION_ID = "tb2-session"
UNSUPPORTED = {"write", "view", "wait", "kill"}

_LOCK = threading.Lock()


class TaskBundle:
    """The task as shipped in the image, with the verifier moved into memory."""

    def __init__(self, task_dir: Path = TASK_DIR):
        meta = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
        self.name: str = meta["name"]
        self.workdir: Path = Path(meta.get("workdir", "/root"))
        self.instructions: dict[str, str] = meta["instructions"]
        self.default_variant: str = meta.get("default_variant", "n")
        self.snapshot: Path = task_dir / "snapshot.tar"
        verifier_dir = task_dir / "verifier"
        self.verifier_tar: bytes = b""
        if verifier_dir.is_dir():
            buf = io.BytesIO()
            with tarfile.open(fileobj=buf, mode="w") as tar:
                tar.add(verifier_dir, arcname=".")
            self.verifier_tar = buf.getvalue()
            if os.environ.get("ARENA_KEEP_VERIFIER") != "1":
                shutil.rmtree(verifier_dir, ignore_errors=True)
        # The reference solution never has to be on disk at run time.
        shutil.rmtree(task_dir / "oracle", ignore_errors=True)

    def instruction(self, variant: str) -> str:
        return self.instructions.get(variant) or self.instructions[self.default_variant]

    def parse_task_id(self, task_id: str | None) -> tuple[str, str]:
        if not task_id:
            return self.name, self.default_variant
        name, sep, variant = task_id.partition("--")
        if name != self.name:
            raise ValueError(f"this image serves task {self.name!r}, not {name!r}")
        variant = variant if sep else self.default_variant
        if variant not in self.instructions:
            raise ValueError(f"unknown variant {variant!r} for task {self.name!r}")
        return name, variant


_BUNDLE: TaskBundle | None = None


def bundle() -> TaskBundle:
    global _BUNDLE
    if _BUNDLE is None:
        _BUNDLE = TaskBundle()
    return _BUNDLE


def cap_output(text: str) -> str:
    if len(text) <= HEAD_CHARS + TAIL_CHARS:
        return text
    cut = len(text) - HEAD_CHARS - TAIL_CHARS
    return text[:HEAD_CHARS] + f"\n...[{cut} characters cut]...\n" + text[-TAIL_CHARS:]


def _kill_group(pid: int) -> None:
    try:
        os.killpg(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def run_shell(command: str, cwd: Path, timeout_s: float) -> tuple[int, str, float]:
    """Run ``command`` with bash in ``cwd``. Returns (status, capped output, seconds)."""
    t0 = time.monotonic()
    proc = subprocess.Popen(
        ["/bin/bash", "-c", command],
        cwd=str(cwd),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    try:
        out, _ = proc.communicate(timeout=timeout_s)
        text = out.decode("utf-8", errors="replace")
        status = proc.returncode
    except subprocess.TimeoutExpired:
        _kill_group(proc.pid)
        out, _ = proc.communicate()
        text = out.decode("utf-8", errors="replace") + f"\n[command timed out after {timeout_s:.0f} s]"
        status = 124
    finally:
        _kill_group(proc.pid)
    return status, cap_output(text), time.monotonic() - t0


class ArenaEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self):
        super().__init__()
        self._bundle = bundle()
        self._episode: dict | None = None
        self._state = Tbench2State(episode_id=None, step_count=0)

    # ----- OpenEnv interface -------------------------------------------------

    def reset(self, seed=None, episode_id=None, task_id=None, **kwargs) -> Tbench2Observation:
        name, variant = self._bundle.parse_task_id(task_id or kwargs.get("task_name"))
        with _LOCK:
            self._restore_workdir()
        self._episode = {
            "task_id": f"{name}--{variant}",
            "variant": variant,
            "instruction": self._bundle.instruction(variant),
            "actions": 0,
            "done": False,
        }
        self._state = Tbench2State(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
            task_id=self._episode["task_id"],
            task_path=str(self._bundle.workdir),
            session_id=SESSION_ID,
            terminal_ready=True,
        )
        return self._observation(output="", action_type="reset", with_instruction=True)

    def step(self, action: Tbench2Action, timeout_s=None, **kwargs) -> Tbench2Observation:
        ep = self._require_episode()
        if ep["done"]:
            return self._observation(
                output="", error="the episode is over", success=False,
                action_type=action.action_type, reward=0.0, done=True,
            )
        ep["actions"] += 1
        self._state.step_count = ep["actions"]
        self._state.last_action_type = action.action_type
        self._state.last_command = action.command

        kind = action.action_type
        if kind == "evaluate":
            return self._finish(kind)
        if kind == "close":
            ep["done"] = True
            return self._observation(output="Closed TB2 environment.", action_type=kind, reward=0.0, done=True)

        output, error, info = "", "", {}
        if kind == "exec":
            if not action.command.strip():
                error = "exec needs a command"
            else:
                status, output, secs = run_shell(action.command, self._bundle.workdir, EXEC_TIMEOUT_S)
                info = {"exit_code": status}
                if status != 0:
                    error = f"command exited with status {status}"
        elif kind == "write_file":
            output, error = self._write_file(action.file_path, action.content)
        elif kind in UNSUPPORTED:
            error = f"{kind} is not available here; use exec, write_file or evaluate"
        else:
            error = f"Unsupported action_type: {kind}"
        self._state.last_output = output

        if ep["actions"] >= MAX_ACTIONS:
            return self._finish(kind, prefix=output + f"\n[action limit of {MAX_ACTIONS} reached]")
        return self._observation(output=output, error=error, success=not error, action_type=kind, info=info)

    @property
    def state(self) -> Tbench2State:
        return self._state

    def close(self) -> None:
        self._episode = None

    # ----- helpers -------------------------------------------------------------

    def _restore_workdir(self) -> None:
        wd = self._bundle.workdir
        for p in (VERIFIER_STAGE, LOGS_DIR):
            shutil.rmtree(p, ignore_errors=True)
        if self._bundle.snapshot.is_file():
            if wd.exists():
                for child in wd.iterdir():
                    if child.is_dir() and not child.is_symlink():
                        shutil.rmtree(child, ignore_errors=True)
                    else:
                        child.unlink(missing_ok=True)
            wd.mkdir(parents=True, exist_ok=True)
            with tarfile.open(self._bundle.snapshot) as tar:
                tar.extractall("/", numeric_owner=True)
        else:
            wd.mkdir(parents=True, exist_ok=True)

    def _write_file(self, file_path: str, content: str) -> tuple[str, str]:
        if not file_path:
            return "", "write_file needs file_path"
        target = Path(file_path)
        if not target.is_absolute():
            target = self._bundle.workdir / target
        real = Path(os.path.realpath(target))
        for forbidden in (ARENA_DIR, VERIFIER_STAGE, LOGS_DIR):
            if real == forbidden or forbidden in real.parents:
                return "", f"cannot write under {forbidden}"
        try:
            real.parent.mkdir(parents=True, exist_ok=True)
            real.write_text(content, encoding="utf-8")
        except OSError as exc:
            return "", f"cannot write {file_path}: {exc.strerror}"
        return f"Wrote {len(content)} characters to {target}", ""

    def _grade(self) -> tuple[float, str]:
        if not self._bundle.verifier_tar:
            return 0.0, "no verifier in this image"
        with _LOCK:
            shutil.rmtree(VERIFIER_STAGE, ignore_errors=True)
            shutil.rmtree(LOGS_DIR, ignore_errors=True)
            VERIFIER_STAGE.mkdir(parents=True)
            LOGS_DIR.mkdir(parents=True)
            with tarfile.open(fileobj=io.BytesIO(self._bundle.verifier_tar)) as tar:
                tar.extractall(VERIFIER_STAGE)
            status, output, secs = run_shell(
                f"bash {VERIFIER_STAGE}/test.sh", self._bundle.workdir, EVAL_TIMEOUT_S
            )
            reward_file = LOGS_DIR / "reward.txt"
            reward = 0.0
            note = f"verifier exited {status} in {secs:.0f}s"
            if reward_file.is_file():
                try:
                    reward = 1.0 if float(reward_file.read_text().strip() or 0) >= 1.0 else 0.0
                except ValueError:
                    note += "; reward.txt unreadable"
            else:
                note += "; no reward.txt"
            shutil.rmtree(VERIFIER_STAGE, ignore_errors=True)
        return reward, note

    def _finish(self, kind: str, prefix: str = "") -> Tbench2Observation:
        ep = self._require_episode()
        reward, note = self._grade()
        ep["done"] = True
        text = (prefix + "\n" if prefix else "") + f"evaluated: reward {reward:g} ({note})"
        return self._observation(output=cap_output(text), action_type=kind, reward=reward, done=True)

    def _require_episode(self) -> dict:
        if self._episode is None:
            raise RuntimeError("call reset(task_id=...) first")
        return self._episode

    def _observation(
        self,
        output: str,
        action_type: str,
        error: str = "",
        success: bool = True,
        reward: float | None = None,
        done: bool = False,
        info: dict | None = None,
        with_instruction: bool = False,
    ) -> Tbench2Observation:
        ep = self._episode or {}
        payload = dict(info or {})
        payload["actions_left"] = max(MAX_ACTIONS - ep.get("actions", 0), 0)
        return Tbench2Observation(
            instruction=ep.get("instruction", "") if with_instruction else "",
            output=output,
            success=success,
            error=error,
            task_id=ep.get("task_id", ""),
            task_path=str(self._bundle.workdir),
            session_id=SESSION_ID,
            action_type=action_type,
            info=payload,
            reward=reward,
            done=done,
        )
