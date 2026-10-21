1. Run `ls /app` and write the 5 library paths to `/app/libraries.txt`. For each lib, AST-scan for public parse/load/decode/validate functions and write `notes_for_testing.txt` using the Fuzzing Target Note template.
2. In each lib run `uv sync` (pyproject) or `uv venv && uv pip install -r requirements.txt`, then `uv pip install -e . atheris` into `/app/<lib>/.venv`.
3. Write `/app/<lib>/fuzz.py`: import atheris, put the lib import inside `instrument_imports()`, add `@atheris.instrument_func` to TestOneInput, catch only expected exceptions, then call `Setup` and `Fuzz`.
4. Run `cd /app/<lib> && .venv/bin/python fuzz.py -max_total_time=10 > fuzz.log 2>&1`, then `tail fuzz.log` for "Done N runs" (fix the driver on spurious exceptions).
