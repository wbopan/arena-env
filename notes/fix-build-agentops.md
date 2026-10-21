**Goal and outputs (restated precisely)**
- Repo: `/home/github/build/failed/<repo>/<id>`. Run `ls /home/github/build/failed/` to find the real `<repo>/<id>`.
- Step 1: write the analysis and plan (root cause, file names, whether it is code or build config) to `/home/github/build/failed/failed_reasons.txt`.
- Step 2: write each change as a git-style unified diff at `/home/github/build/failed/<repo>/<id>/patch_1.diff`, `patch_2.diff`, and so on. Each diff needs:
  - `--- a/path` and `+++ b/path` headers, with paths relative to the repo root;
  - `@@ -l,n +l,n @@` hunks with correct line counts;
  - context lines that start with a space;
  - a trailing newline at the end of the file.
- Step 3: apply the diffs to the repo, so the working tree contains the fixes.

**Cheap inspection (no full-file dumps)**
- `cd` into the repo, then get an overview:
  - `git log --oneline -3; git status --short | head`
  - `ls -a`
  - `ls .github/workflows`
- Read the CI definition to learn the exact commands CI runs:
  - `grep -nE "run:|python-version|uv |pip |pytest|ruff|mypy|pyright" .github/workflows/*.yml | head -40`
- Look for local evidence of the failure:
  - `ls` for any `*.log` or failure file;
  - `find / -name "*.log" -path "*build*" 2>/dev/null | head`
- The analyze-ci skill (`uv run skills analyze-ci <url>`) needs network access and a GitHub token. It is likely unavailable here, so reproduce the failure locally instead.
- Check the project configuration:
  - `sed -n '1,80p' pyproject.toml`, or grep for the `[tool.pytest.ini_options]`, `[project]`, `dependencies` and `requires-python` sections;
  - look for `uv.lock`, `setup.cfg`, `tox.ini`, `pytest.ini`, `.pre-commit-config.yaml`.

**Reproduce the failure the way CI does**
- With uv: `uv sync` (or `uv sync --all-extras --dev`), then `uv run pytest -x -q 2>&1 | tail -40`.
- Without uv: `pip install -e ".[dev]"`, then `python -m pytest -x -q 2>&1 | tail -40`.
- If CI runs lint or type checks, run those too: `uv run ruff check . | tail`, `uv run ruff format --check`, `mypy`/`pyright`.
- If the network is down, skip installs and just run what is installed. Use `python -c "import pkg"` to surface ImportErrors.
- Always pipe output through `tail`/`head`. Use `grep -n` on error lines, then `sed -n 'A,Bp' file` around the reported line numbers.

**Common failure categories and how to tell them apart**
- **Code errors**:
  - SyntaxError, NameError, ImportError (renamed or moved symbol, missing import);
  - wrong function signature;
  - a test assertion that no longer matches the code;
  - type-check errors;
  - ruff lint errors such as unused imports, import order, or line length.
- **Build/config errors**:
  - missing dependency in `pyproject.toml`;
  - wrong version pin or incompatible library API;
  - bad `build-backend` (e.g. it must be `setuptools.build_meta`, not `setuptools.build_backend`);
  - stale `uv.lock`;
  - `requires-python` mismatch;
  - pytest config problems: `asyncio_mode = "auto"` missing while tests are async without markers; `--strict-markers` with an unregistered marker; a `--cov-fail-under` threshold; an unknown option in `addopts`;
  - missing plugin (pytest-asyncio, pytest-xdist for `-n auto`, pytest-cov, inline-snapshot).
- **Async/pytest facts from the skills**:
  - With `asyncio_mode = "auto"`, async tests need no `@pytest.mark.asyncio`.
  - Async fixtures require pytest-asyncio.
  - Set `asyncio_default_fixture_loop_scope = "function"` to silence the deprecation warning. That warning becomes an error when `filterwarnings = error` is set.
  - A session-scoped `event_loop` fixture is deprecated in new pytest-asyncio.
- **Temporal-specific facts**, if the repo uses temporalio:
  - Tests use `WorkflowEnvironment.start_time_skipping()` and `ActivityEnvironment().run(fn, args)`.
  - Workflow code must be deterministic: use `workflow.now()` and `workflow.random()`, never `datetime.now()` or `random`.
  - Activities must be decorated with `@activity.defn` and workflows with `@workflow.defn`/`@workflow.run`.
  - `execute_activity` needs `start_to_close_timeout` or `schedule_to_close_timeout`.
  - Time-skipping downloads a test server binary, so a network failure there is environmental, not a code bug.

**Making the fix with minimal tokens**
- Make the smallest change that fixes the root cause. Do not refactor, and do not delete or skip tests to make CI pass.
- Recommended diff workflow, using git to generate a correct format:
  ```
  cp file file.orig   # or rely on git
  # edit with python/sed
  python - <<'EOF'
  import re,pathlib
  p=pathlib.Path("src/pkg/mod.py"); s=p.read_text()
  s=s.replace("old text","new text",1); p.write_text(s)
  EOF
  git diff -- src/pkg/mod.py > patch_1.diff
  ```
  Then verify that the patch round-trips:
  ```
  git stash
  git apply --check patch_1.diff && git apply patch_1.diff
  ```
  Or, more simply, reset and re-apply: `git checkout -- file && git apply patch_1.diff`.
- Use one diff per logical change or per file: `patch_1.diff`, `patch_2.diff`, …
- If the repo is not a git repo, use `diff -u a/file b/file` with an `a/` and `b/` copy, then apply with `patch -p1 < patch_1.diff`.
- Make sure the patch files themselves do not get included in later `git diff` outputs. Write each diff before creating the next one, or limit `git diff` to specific paths.

**Step-by-step plan (about 20 commands)**
1. Locate the repo with `ls`. Read the CI workflow's run lines, `pyproject.toml` (head), and git status.
2. Reproduce the failing command (tests, lint, or build) with output tailed, and note the exact error and the file:line.
3. Inspect only the relevant lines with `sed -n`/`grep -n`. Decide whether the cause is code or config.
4. Write `failed_reasons.txt` containing:
   - the error message;
   - the root cause;
   - code vs config;
   - the planned edits per file.
5. Edit the files. Generate `patch_i.diff` with `git diff -- <file>`, and confirm the patches are applied in the working tree.
6. Re-run the same CI command(s) and confirm they pass, or that only network/environment issues remain. Also run lint if CI lints.
7. Final check:
   - `ls /home/github/build/failed/<repo>/<id>/patch_*.diff`;
   - `head` one diff to confirm its headers;
   - `git diff --stat` to confirm the changes are in place.
