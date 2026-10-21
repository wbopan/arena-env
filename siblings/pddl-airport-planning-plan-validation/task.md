# Validate candidate airport ground-traffic plans

This is a STRIPS planning task with typing.

## Inputs (in /root/work)

- `domain.pddl`: the airport ground-traffic domain, with actions `move`, `takeoff` and `park`.
- `problem.pddl`: a problem with typed objects, an `:init` state and a conjunctive `:goal`.
- `plans/plan_*.txt`: candidate plans.
  - Each plan has one action per line, written as `name(arg1, arg2, ...)`.
  - Blank lines and lines starting with `;` are ignored.
  - Steps are numbered from 1, counting only action lines.

## What to do

Simulate each plan from the initial state using standard sequential STRIPS semantics:

- A step is applicable if all of its grounded preconditions hold.
- When a step is applied, delete effects are removed first and then add effects are added.

A step is `invalid_action` if any of the following holds:

- the line is malformed,
- the action name is unknown,
- the number of arguments is wrong,
- an argument is not a declared object,
- an argument's declared type differs from the parameter's type.

Simulation stops at the first step that is `invalid_action`, or whose preconditions fail (`precondition`). If every step is applied but some goal atom is false at the end, the reason is `goal`.

## Output

Write `/root/work/validation.json`: a JSON object keyed by plan file name (for example `"plan_01.txt"`). Each value is:

```json
{"valid": true|false, "failed_step": int|null, "reason": "invalid_action"|"precondition"|"goal"|null, "goals_satisfied": int}
```

- `failed_step` is the 1-based index of the failing step. It is null when the plan is valid or the reason is `goal`.
- `reason` is null when the plan is valid.
- `goals_satisfied` is the number of goal atoms true in the last state reached. On a step failure, this is the state just before the failing step.

Names are case-insensitive; all inputs use lowercase.
