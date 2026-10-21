**Goal.** For every entry in `problem.json` (keys `id`, `domain`, `problem`, `plan_output`), read both PDDL files, find a valid sequential plan, and write it to `plan_output`. Write one action per line in the form `name(arg1, arg2, ...)`, for example `move(a, b)`. Action and object names must match the PDDL files exactly. Create parent directories if they are missing. No header or footer is needed.

**Domain facts (IPC airport ground traffic).**
- Typical actions are `move`, `pushback`, `startup`, `park` and `takeoff`. Their parameters are an airplane, segments and directions, and possibly an airplane type.
- The STRIPS version uses typing only. Some versions are ADL, with `forall`/`when` blocking effects or negative preconditions.
- Pyperplan handles STRIPS with typing only. If the domain contains `:conditional-effects`, `forall`, `when` or negation, pyperplan will refuse it.
- Large instances (Munich) can blow up the grounding and the search. Use a timeout and keep a fallback planner ready.

**Cheap inspection (do not cat whole files):**
```
cat problem.json | head -c 600; python3 -c "import json;d=json.load(open('problem.json'));print(len(d))"
head -40 <domain.pddl>; grep -n ":requirements\|:action" <domain.pddl>
wc -c <problem.pddl>; grep -c "" <problem.pddl>
python3 -c "import unified_planning.shortcuts as s;print(s.get_environment().factory.engines)"
which fast-downward downward 2>/dev/null; pip list 2>/dev/null | grep -i -E "up-|pyperplan|fast|enhsp|tamer"
```

**Library calls that work (unified_planning):**
```python
import json, os, sys
from unified_planning.io import PDDLReader
from unified_planning.shortcuts import OneshotPlanner, SequentialPlanValidator, get_environment
get_environment().credits_stream = None

def solve(dom, prob):
    p = PDDLReader().parse_problem(dom, prob)
    for name in ["pyperplan", "fast-downward", "enhsp", "tamer"]:   # keep only installed ones
        try:
            with OneshotPlanner(name=name) as pl:
                r = pl.solve(p, timeout=300)
            if r.plan is not None:
                with SequentialPlanValidator(problem_kind=p.kind) as v:
                    if v.validate(p, r.plan).status.name == "VALID":
                        return p, r.plan
        except Exception as e:
            print(name, "failed:", e, file=sys.stderr)
    return p, None

def fmt(ai):
    return f"{ai.action.name}({', '.join(str(x) for x in ai.actual_parameters)})"

for t in json.load(open("problem.json")):
    p, plan = solve(t["domain"], t["problem"])
    os.makedirs(os.path.dirname(t["plan_output"]) or ".", exist_ok=True)
    with open(t["plan_output"], "w") as f:
        if plan:
            f.write("\n".join(fmt(a) for a in plan.actions) + "\n")
    print(t["id"], "OK" if plan else "NO PLAN", len(plan.actions) if plan else 0)
```

**Notes on these calls:**
- Without a `name=`, `OneshotPlanner(problem_kind=p.kind)` auto-selects any installed engine that supports the problem's features. It is a useful fallback when pyperplan rejects ADL.
- `str(param)` on an `actual_parameters` entry gives the object name. If you see quotes or odd prefixes, use `x.object().name` instead.
- `PDDLWriter(p).write_plan(plan, path)` writes the `(move a b)` s-expression format. The example in the task uses the `name(a, b)` format, so use the manual `fmt` above to match it.
- If UP renamed identifiers during parsing (rare, for hyphen or keyword clashes), map back using the original names from the PDDL. Grep the output against `grep -o "(:action [^ ]*"` on the domain to confirm the names agree.

**Pitfalls:**
- Pyperplan uses blind or weak search by default and may be very slow on big airport instances. Pass a timeout and fall back to fast-downward or enhsp if they are installed.
- Fast Downward may also be available as a CLI: `fast-downward.py dom prob --search "lama-first()"`. It writes `sas_plan` as `(move a b)` lines. Convert each line to `move(a, b)` and keep only lines that start with `(`, dropping the `; cost` comment.
- If no planner can handle the domain and nothing is installed, an emergency option is a small Python BFS/greedy search over grounded STRIPS actions. Only attempt this for small instances.
- PDDL is case-insensitive, but keep names exactly as UP reports them (usually lowercase, as in the files).
- Never write an empty file silently. Report failures, and retry with another engine or a longer timeout.

**Step-by-step plan:**
1. Inspect `problem.json` (count the entries, view one), the domain's `:requirements` and action headers, the problem sizes, and the installed engines.
2. Write `solve.py` as above, listing only the installed engines and putting the fastest suitable one first.
3. Run it with a generous overall timeout, for example `timeout 1500 python3 solve.py`, and watch the per-task OK / NO PLAN lines.
4. Check the output:
   - `head -3` each plan file.
   - Confirm every line matches `^[a-z0-9_-]+\(.*\)$`.
   - Confirm the action names appear in the domain.
5. Re-validate by re-parsing the written files. Build the actions with `p.action(name)` and `p.object(o)` into `SequentialPlan([ActionInstance(...)])`, then run `SequentialPlanValidator`. Alternatively, trust the in-loop validation, provided the formatting step only reprints the same plan.
6. For any task that failed, retry with a different engine or a longer timeout until every `plan_output` holds a validated plan.
