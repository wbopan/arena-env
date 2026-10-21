1. `ls /home/github/build/failed/`, then in the repo grep `.github/workflows/*.yml` for run commands and read `pyproject.toml` with head.
2. Reproduce the CI step (`uv run pytest -x -q` / `ruff check`) and `| tail -40`; find the code-vs-config root cause with grep/sed.
3. Write the analysis to `/home/github/build/failed/failed_reasons.txt`, then make a minimal edit with python/sed.
4. Save each change as `git diff -- <file> > <repo>/<id>/patch_N.diff` and make sure it is applied (`git apply --check` round-trip).
5. Re-run the failing command to confirm it passes.
