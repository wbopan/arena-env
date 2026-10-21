**Goal.** For every entry in `problem.json`, read the `domain` and `problem` PDDL files, find a valid sequential plan, and write it to that entry's `plan_output` path. Write one action per line in function-call style, matching the task's example:
```
drive(truck1, depot1, market1)
buy(truck1, goods1, market1, level0, level1, level0, level1)
```
Action and object names must match the PDDL exactly (lowercase as in the files). Do not add parentheses around the whole line, and do not add comments, costs or headers. Create parent directories if they are missing.

**Tools (from the skill): the `unified_planning` (UP) Python library.**
- Load: `from unified_planning.io import PDDLReader; prob = PDDLReader().parse_problem(domain_path, problem_path)`
- Plan: `from unified_planning.shortcuts import OneshotPlanner; with OneshotPlanner(name="pyperplan") as p: res = p.solve(prob)`. Then `res.plan` is a `SequentialPlan`, or None. Check `res.status`.
- Validate: `from unified_planning.shortcuts import PlanValidator; with PlanValidator(name="sequential_plan_validator") as v: ok = v.validate(prob, plan).status.name == "VALID"`. Alternatively, use `PlanValidator(problem_kind=prob.kind)`.
- Silence the credits banner: `from unified_planning.shortcuts import get_environment; get_environment().credits_stream = None`.

**Output-format pitfall.** `PDDLWriter().write_plan` produces `(drive truck1 depot1 market1)`. That is s-expression style, not the required style. Format each action yourself:
```python
line = f"{ai.action.name}({', '.join(str(p) for p in ai.actual_parameters)})"
```
`str(p)` on an object parameter gives the bare object name. Check one line visually after writing.

**Domain facts (TPP, STRIPS with levels).**
- Trucks drive between places (depots and markets).
- `buy` uses goods/market quantity levels and `next` facts.
- `load` and `unload` also use level parameters, so actions have many parameters.
- Goals are stored goods levels at depots.

The plan only needs to be valid; it does not need to be optimal. Pyperplan, the skill's default, may be slow on larger instances.

If pyperplan times out or is not installed, list the installed engines:
```
python -c "from unified_planning.shortcuts import get_environment as g; print(g().factory.engines)"
```
Then try other engines in order:
1. `fast-downward` (fast, recommended if present)
2. `enhsp`
3. `OneshotPlanner(problem_kind=prob.kind)` (auto-select)

Wrap each attempt in try/except and move on to the next engine on failure. Pass a timeout to `solve` if the engine supports it (`p.solve(prob, timeout=...)`). If the engine doesn't support it, run each task in a subprocess with `timeout`.

**Step-by-step plan (keep output small).**
1. `cat problem.json | head -c 1500` and `python -c "import json;d=json.load(open('problem.json'));print(len(d));print(d[0])"`. Locate `problem.json` first with `ls` or `find / -name problem.json 2>/dev/null | head`. Check whether the paths are relative; if so, resolve them relative to the directory of `problem.json`.
2. Peek at one domain cheaply: `grep -n ":action" domain.pddl` and `head -40 domain.pddl`. Get problem sizes with `wc -l`. Do not cat whole files.
3. Check the library: `python -c "import unified_planning, up_pyperplan; print('ok')"`. If pyperplan is missing, try `pip install unified-planning up-pyperplan` (or `up-fast-downward`).
4. Write a single script `solve.py`:
```python
import json, os, sys
from unified_planning.io import PDDLReader
from unified_planning.shortcuts import OneshotPlanner, PlanValidator, get_environment
get_environment().credits_stream = None
tasks = json.load(open(sys.argv[1]))
base = os.path.dirname(os.path.abspath(sys.argv[1]))
R = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
for t in tasks:
    prob = PDDLReader().parse_problem(R(t["domain"]), R(t["problem"]))
    plan = None
    for eng in ["fast-downward", "pyperplan", None]:
        try:
            kw = {"name": eng} if eng else {"problem_kind": prob.kind}
            with OneshotPlanner(**kw) as p:
                r = p.solve(prob)
            if r.plan is not None:
                plan = r.plan; break
        except Exception as e:
            print(t["id"], eng, "err", type(e).__name__)
    if plan is None:
        print(t["id"], "NO PLAN"); continue
    with PlanValidator(name="sequential_plan_validator") as v:
        ok = v.validate(prob, plan).status.name
    out = t["plan_output"]  # use as given; if relative, consider R(out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as f:
        for ai in plan.actions:
            f.write(f"{ai.action.name}({', '.join(str(p) for p in ai.actual_parameters)})\n")
    print(t["id"], ok, len(plan.actions))
```
5. Run it and look only at the one-line-per-task summary. Every task must report VALID.
6. Verify the files: `ls -l` the outputs and `head -3` one of them. Confirm the lines look like `name(a, b, c)` and the file ends with a newline.
7. If a task fails or times out, rerun only that task with another engine. Do not leave any `plan_output` missing or empty.

**Pitfalls.**
- Keep `plan_output` exactly as given; the grader reads it from there. If the path is relative, the working directory matters: run from the directory where `problem.json` lives, or the task root.
- The planner engine's own name prints aren't needed; suppress verbose output.
- Never hand-edit names. Use the names UP parsed from the PDDL.
