1. Inspect `problem.json` and the domain's `:requirements` and actions with head/grep, and list the installed UP engines (pyperplan only handles STRIPS; fall back to fast-downward or enhsp, or `OneshotPlanner(problem_kind=p.kind)` with no name, for ADL or large instances).
2. Write one script: `PDDLReader().parse_problem(dom, prob)`, then `OneshotPlanner(name=...)` with a timeout, then `SequentialPlanValidator`.
3. Write each action as `name(arg1, arg2)`, one per line, to that task's `plan_output`.
4. Check the line format and confirm every task reports VALID; retry failures with another engine.
