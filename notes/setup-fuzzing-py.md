**Goal artifacts (exact paths):**
- `/app/libraries.txt`: one library path per line, for the 5 library directories under `/app/` (e.g. `/app/<lib>`). Skip non-library dirs such as `.venv`, hidden dirs and tooling.
- `/app/<lib>/notes_for_testing.txt`: the functions under test, using the "Fuzzing Target Note" template described below.
- `/app/<lib>/fuzz.py`: the Atheris/LibFuzzer driver.
- `/app/<lib>/.venv`: the virtualenv inside each library root, with the deps, the library itself and atheris installed.
- `/app/<lib>/fuzz.log`: the log of a roughly 10-second fuzz run, written after the run finishes.

**Inspect cheaply (do not cat whole files):**
- List the top level: `ls /app`. Then for each lib, list it with `ls /app/<lib>` or `tree -L 2 /app/<lib>` piped through `| head -50`.
- Find the packaging files: `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements*.txt`. Skim them with `head -40`.
- Find the import name. It is the package dir in a flat layout, or `src/<pkg>` in a src layout. Check `__init__.py` with `grep -n "__all__\|^from\|^def" __init__.py | head`.
- Find candidate functions with an AST header scan instead of reading bodies:
  ```
  python3 - <<'E'
  import ast,sys,glob
  for f in glob.glob('/app/LIB/**/*.py',recursive=True):
    if '/test' in f or '.venv' in f: continue
    t=ast.parse(open(f).read())
    for n in ast.walk(t):
      if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and not n.name.startswith('_'):
        print(f.split('/app/')[1],n.lineno,n.name)
  E
  ```
  Pipe the output through `| grep -iE "parse|load|decode|loads|validate|from_|normalize|read" | head -30`.
- Check the tests for usage and seed inputs: `grep -rn "import\|<func>(" tests | head`.

**Choosing functions under test (skill rubric):**
- Prefer public entry points that take str or bytes and parse, decode, deserialize, validate or normalize.
- Prefer targets reachable with little setup.
- Prefer high boundary risk: parsers and native bindings.
- Prefer code with weak test coverage.
- Keep 1–5 per library.

**Notes file content:**
Write each FUT as a block with these fields:
- **Target:** qualname.
- **File / location:** file and line.
- **Why this target:** input surface, boundary/native, complexity, test gaps.
- **Callable contract:** imports, preconditions, determinism, external deps.
- **Input model:** payload type, decoding steps, constraints, edge classes.
- **Oracles:** must-hold properties (round-trip, idempotence, no crash), acceptable exceptions, suspicious exceptions, crash-only vs correctness-checking.
- **Harness plan:** approach, signature `TestOneInput(data: bytes)`, seed ideas, timeouts.
- **Risk flags:** native, DoS, I/O.
- **Next actions:** numbered list.

Writing these via a heredoc (`cat > file <<'EOF'`) is fine. Optionally also write `APIs.txt` in the repo root.

**Env setup (uv skill):**
- If `pyproject.toml` exists: `cd /app/<lib> && uv sync`. That creates `.venv`. Then run `uv pip install atheris` (it targets `.venv` automatically), or use `uv add atheris`.
- If only `requirements.txt` exists: `cd /app/<lib> && uv venv && uv pip install -r requirements.txt && uv pip install atheris`. Install the lib itself too with `uv pip install -e .` if it has setup.py or pyproject.
- If neither exists: run `uv venv`, install atheris, and rely on running from the lib dir so the package is importable. Add `sys.path.insert(0, os.path.dirname(__file__))` in fuzz.py.
- If `uv sync` fails, fall back to `uv venv && uv pip install -e . atheris`. If uv is missing, use `python3 -m venv .venv && .venv/bin/pip install ...`.
- Sanity checks: `test -x .venv/bin/python` and `.venv/bin/python -c "import atheris, <pkg>"`.

**Driver template (`fuzz.py`):**
```python
#!/usr/bin/env python3
import sys, os
import atheris
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
with atheris.instrument_imports():
    import mypkg

@atheris.instrument_func
def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    s = fdp.ConsumeUnicodeNoSurrogates(fdp.remaining_bytes())  # or pass raw bytes
    try:
        mypkg.parse(s)
    except (ValueError, TypeError, KeyError):   # documented/expected errors only
        pass

def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()

if __name__ == "__main__":
    main()
```
**Driver pitfalls:**
- Import atheris first, and import the target library inside `instrument_imports()`.
- `@atheris.instrument_func` on TestOneInput avoids "no interesting inputs were found".
- Catch only the library's documented exceptions, such as its own `*Error` classes. Uncaught exceptions are reported as crashes.
- Never call `sys.exit` inside the target. Keep it deterministic and fast.
- You can exercise several FUTs by choosing one with `fdp.ConsumeIntInRange(0, n-1)`. A round-trip check (`loads(dumps(x)) == x`) can serve as an oracle.
- Wrap RecursionError only if it is expected.

**Running (10 s per library):**
```
cd /app/<lib> && .venv/bin/python fuzz.py -max_total_time=10 > fuzz.log 2>&1
```
- Equivalently: `uv run -- python fuzz.py -max_total_time=10 &> fuzz.log`.
- libFuzzer writes its stats to stderr, so redirect both stdout and stderr.

**Checking the log:**
- Run `tail -5 fuzz.log` and look for `INITED cov:` lines, `pulse`/`NEW` lines and a `Done N runs in 10 second(s)` line.
- If you see "Uncaught Python exception", read the traceback with `grep -A15 "Uncaught" fuzz.log`.
  - An expected or benign exception type means the driver is over-strict: add it to the except clause and rerun.
  - A genuine crash can stay, but the run must still show the fuzzer working.
- Delete stray `crash-*` files only if they come from driver mistakes.

**Step-by-step plan:**
1. Run `ls /app`, pick the 5 library dirs, and write `/app/libraries.txt`.
2. For each lib, read packaging file heads and run the AST scan and test grep. Then write `notes_for_testing.txt`.
3. Create `.venv` with uv, install deps, the lib and atheris, then verify the import.
4. Write `fuzz.py` using the real function names and signatures. Use `sed -n 'a,bp'` on the target function to confirm argument types.
5. Run with `-max_total_time=10` into `fuzz.log`, then `tail` it to confirm.
6. Final check: `for d in $(cat /app/libraries.txt); do ls -a $d | grep -E "notes_for_testing|fuzz.py|fuzz.log|.venv"; done`.
