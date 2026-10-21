1. Run `cat -n /app/workspace/solution.lean | head -30` and back it up to /tmp. Note S's type, its recursion style, and that the proof starts at line 15.
2. With Python, keep the original lines 1–14 verbatim and append a tactic proof:
   - `have h : ∀ m, S m = 2 - 1/2^m` by `induction` (`norm_num [S]` for zero; `rw [S, ih]; ring` for succ, with `field_simp` as backup);
   - then `rw [h n]`, `positivity` for `0 < 1/2^n`, and `linarith`.
3. Compile with `lake env lean solution.lean` from the project root. The output must be completely empty: no errors, no warnings, no sorry.
4. Check the prefix with `diff` against the backup, and grep the file for `sorry`/`exact?`.
