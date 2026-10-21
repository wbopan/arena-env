"""
Play a Qwen3.8-27B-compatible model against task images under the arena's
episode rules, one fresh container per episode, to measure solve rates and
how episodes end. Ported from rca-umb's calibrate_tb2.py (Apache-2.0).

Arena rules: the user turn is the observation JSON; every reply must be exactly
one JSON object (an action, or {"finish": true}); any other reply ends the
episode, which is then scored through the finish action (`evaluate`).
`completion_tokens` covers the model's tokens and every observation after the
first; `context_tokens` covers the whole conversation; tool calls are capped.
Token counts use the Qwen3.8 tokenizer (`--tokenizer`, a tokenizer.json).

The API key is read from the file --key-file names and never printed.

Usage:
  python calibrate.py --tasks invoice-fraud-detection--n,invoice-fraud-detection--s \
      --episodes 8 --parallel 4 --tokenizer tokenizer.json --out cal/run1 \
      --base-url https://openrouter.ai/api/v1 --model qwen/qwen3.8-27b \
      --key-file ~/.config/openrouter/key --extra-body '{"reasoning":{"enabled":false}}'
"""

import argparse
import json
import random
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pydantic import ValidationError  # noqa: E402
from tokenizers import Tokenizer  # noqa: E402

from arena_env.models import Tbench2Action  # noqa: E402
from wsclient import Session  # noqa: E402

FINISH_ACTION = {"action_type": "evaluate"}
TEMPLATE_TOKENS = 5  # role markers per chat message


def system_prompt(schema: dict) -> str:
    return ("You are an agent acting in an environment. Reply to every message with exactly one JSON object and "
            "nothing else: an action that matches the action schema below, or {\"finish\": true} to end the episode.\n"
            f"Action schema: {json.dumps(schema)}")


def parse_strict(text: str):
    try:
        obj = json.loads(text.strip())
    except (json.JSONDecodeError, ValueError):
        return None
    return obj if isinstance(obj, dict) else None


def parse_lenient(text: str):
    dec = json.JSONDecoder()
    for i, ch in enumerate(text or ""):
        if ch == "{":
            try:
                obj, _ = dec.raw_decode(text[i:])
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                continue
    return None


class Model:
    def __init__(self, base_url, model, temperature, key_file, extra_body):
        self.api = base_url.rstrip("/") + "/chat/completions"
        self.model, self.temperature, self.extra = model, temperature, extra_body
        self._key = Path(key_file).expanduser().read_text().strip() if key_file else ""
        self.usage = {"prompt_tokens": 0, "completion_tokens": 0, "calls": 0, "retries": 0}
        self._lock = threading.Lock()

    def chat(self, messages, max_tokens):
        body = {"model": self.model, "messages": messages, "max_tokens": max_tokens,
                "temperature": self.temperature, **self.extra}
        headers = {"Content-Type": "application/json", "User-Agent": "arena-env-calibration/1.0"}
        if self._key:
            headers["Authorization"] = f"Bearer {self._key}"
        for attempt in range(8):
            req = urllib.request.Request(self.api, data=json.dumps(body).encode(), headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=300) as r:
                    data = json.load(r)
                break
            except urllib.error.HTTPError as exc:
                if exc.code in (429, 500, 502, 503, 504) and attempt < 7:
                    with self._lock:
                        self.usage["retries"] += 1
                    time.sleep(min(60, 2 ** attempt * 2) + random.random())
                    continue
                raise RuntimeError(f"inference HTTP {exc.code}: {exc.read().decode()[:200]}") from None
            except (urllib.error.URLError, TimeoutError):
                if attempt < 7:
                    time.sleep(2 ** attempt)
                    continue
                raise
        u = data.get("usage") or {}
        with self._lock:
            self.usage["prompt_tokens"] += u.get("prompt_tokens", 0)
            self.usage["completion_tokens"] += u.get("completion_tokens", 0)
            self.usage["calls"] += 1
        ch = data["choices"][0]
        return ch["message"].get("content") or "", u.get("completion_tokens", 0), ch.get("finish_reason")


class Container:
    """One task image, started on a free port, removed on exit."""

    def __init__(self, image: str, cpus: str = "2", memory: str = "8g"):
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            self.port = s.getsockname()[1]
        self.cid = subprocess.check_output(
            ["docker", "run", "-d", "--rm", f"--cpus={cpus}", f"--memory={memory}",
             "-p", f"127.0.0.1:{self.port}:8000", image], text=True).strip()
        self.url = f"http://127.0.0.1:{self.port}"
        for _ in range(120):
            try:
                with urllib.request.urlopen(self.url + "/health", timeout=2):
                    return
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                time.sleep(1)
        self.close()
        raise RuntimeError(f"{image}: server never became healthy")

    def close(self):
        subprocess.run(["docker", "rm", "-f", self.cid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def play(url, model, tok, schema, task_id, budgets, lenient=False):
    """lenient=True takes the first JSON object in a reply (what a policy that has
    learned the reply format would have sent); the strict verdict is kept in ep["strict_end"]."""
    comp_budget, ctx_budget, max_calls = budgets
    ntok = lambda s: len(tok.encode(s).ids) + TEMPLATE_TOKENS  # noqa: E731
    messages = [{"role": "system", "content": system_prompt(schema)}]
    ctx = ntok(messages[0]["content"])
    used = 0
    ep = {"task_id": task_id, "turns": [], "end": None, "reward": 0.0, "lenient_would_parse": 0}
    with Session(url, timeout=200) as s:
        data = s.reset(task_id=task_id)
        obs = data["observation"]
        calls = 0
        while True:
            text = json.dumps({k: v for k, v in obs.items() if k not in ("metadata", "reward", "done") or v})
            t = ntok(text)
            if len(messages) > 1:
                used += t
            ctx += t
            if used >= comp_budget or ctx >= ctx_budget:
                ep["end"] = "budget"
                data = s.step(FINISH_ACTION)
                break
            messages.append({"role": "user", "content": text})
            room = min(comp_budget - used, ctx_budget - ctx)
            reply, n, finish = model.chat(messages, room)
            used += n
            ctx += n + TEMPLATE_TOKENS
            messages.append({"role": "assistant", "content": reply})
            ep["turns"].append({"obs_tokens": t, "obs": text[:600], "reply": reply[:1500], "reply_tokens": n, "finish": finish})
            if finish == "length":
                ep["end"] = "reply_cut"
                data = s.step(FINISH_ACTION)
                break
            action = parse_strict(reply)
            if action is None and lenient:
                action = parse_lenient(reply)
                if action is not None:
                    ep["lenient_turns"] = ep.get("lenient_turns", 0) + 1
                    ep.setdefault("strict_end", "invalid_reply")
            if action is None:
                ep["end"] = "empty_reply" if not reply.strip() else "invalid_reply"
                ep["lenient_would_parse"] = int(parse_lenient(reply) is not None)
                data = s.step(FINISH_ACTION)
                break
            if set(action) == {"action"} and isinstance(action["action"], dict):
                action = action["action"]
            if action.get("finish") is True:
                ep["end"] = "finish"
                data = s.step(FINISH_ACTION)
                break
            try:
                Tbench2Action.model_validate(action)
            except ValidationError:
                ep["end"] = "schema_invalid"
                data = s.step(FINISH_ACTION)
                break
            calls += 1
            data = s.step(action)
            obs = data["observation"]
            if data["done"]:
                ep["end"] = "evaluated" if action.get("action_type") in ("evaluate", "close") else "done"
                break
            if calls >= max_calls:
                ep["end"] = "out_of_calls"
                data = s.step(FINISH_ACTION)
                break
    ep["reward"] = data.get("reward") or 0.0
    ep.setdefault("strict_end", ep["end"])
    ep["n_calls"] = calls
    ep["completion_used"] = used
    ep["context_used"] = ctx
    ep["final_output"] = (data.get("observation") or {}).get("output", "")[:300]
    return ep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True, help="comma-separated task ids (<name>--<variant>) or @file")
    ap.add_argument("--image-prefix", default="arena-task/")
    ap.add_argument("--image-tag", default="local")
    ap.add_argument("--episodes", type=int, default=4)
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--base-url", default="https://openrouter.ai/api/v1")
    ap.add_argument("--model", default="qwen/qwen3.8-27b")
    ap.add_argument("--key-file", default="~/.config/openrouter/key")
    ap.add_argument("--extra-body", default='{"reasoning":{"enabled":false}}')
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--completion-budget", type=int, default=4096)
    ap.add_argument("--context-budget", type=int, default=8192)
    ap.add_argument("--max-calls", type=int, default=32)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lenient", action="store_true", help="accept the first JSON object in a reply")
    args = ap.parse_args()
    if args.tasks.startswith("@"):
        tasks = [l.strip() for l in Path(args.tasks[1:]).read_text().splitlines() if l.strip() and not l.startswith("#")]
    else:
        tasks = args.tasks.split(",")
    tok = Tokenizer.from_file(args.tokenizer)
    model = Model(args.base_url, args.model, args.temperature, args.key_file, json.loads(args.extra_body))
    budgets = (args.completion_budget, args.context_budget, args.max_calls)
    schema_cache = {}
    schema_lock = threading.Lock()

    def job(task_id):
        name = task_id.split("--")[0]
        c = Container(f"{args.image_prefix}{name}:{args.image_tag}")
        try:
            with schema_lock:
                if name not in schema_cache:
                    with urllib.request.urlopen(f"{c.url}/schema", timeout=15) as r:
                        schema_cache[name] = json.load(r)["action"]
            return play(c.url, model, tok, schema_cache[name], task_id, budgets, args.lenient)
        finally:
            c.close()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    results = []
    with ThreadPoolExecutor(args.parallel) as ex, open(out / "episodes.jsonl", "a") as log:
        futs = [ex.submit(job, t) for _ in range(args.episodes) for t in tasks]
        for f in futs:
            try:
                ep = f.result()
            except Exception as exc:  # infrastructure errors are excluded, not scored as 0
                print("episode error:", repr(exc)[:300], file=sys.stderr)
                continue
            results.append(ep)
            log.write(json.dumps(ep) + "\n")
            log.flush()
    summary = {}
    for t in tasks:
        eps = [e for e in results if e["task_id"] == t]
        if not eps:
            continue
        ends = {}
        for e in eps:
            ends[e["end"]] = ends.get(e["end"], 0) + 1
        summary[t] = {"n": len(eps), "solved": sum(e["reward"] >= 1.0 for e in eps),
                      "strict_ok": sum(e["strict_end"] == e["end"] for e in eps),
                      "mean": round(mean(e["reward"] for e in eps), 3),
                      "ends": ends, "calls": round(mean(e["n_calls"] for e in eps), 1),
                      "completion_used": round(mean(e["completion_used"] for e in eps))}
    report = {"model": args.model, "episodes": len(results), "seconds": round(time.monotonic() - started),
              "usage": model.usage, "budgets": budgets, "tasks": summary}
    (out / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    for t, s in summary.items():
        print(f"{t:44s} solved {s['solved']}/{s['n']}  calls {s['calls']:4.1f}  used {s['completion_used']:5d}  {s['ends']}")
    print("usage:", model.usage, "seconds:", report["seconds"])


if __name__ == "__main__":
    main()
