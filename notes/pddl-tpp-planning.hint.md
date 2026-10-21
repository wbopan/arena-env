1. Find and inspect `problem.json` (count the tasks, check whether paths are relative), then `grep ":action"` one domain.
2. Write one Python script: `PDDLReader().parse_problem(domain, problem)`, then `OneshotPlanner` (fast-downward if available, else pyperplan).
3. Validate each plan with `PlanValidator(name="sequential_plan_validator")`.
4. Write each action as `name(arg1, arg2, ...)`, one per line, to `plan_output`, creating directories as needed. Do not use `PDDLWriter`'s `(name a b)` format.
5. Run, confirm every task prints VALID, then `head -3` one output file.
