# Validate candidate TPP plans against a PDDL problem

Inputs in `/root/work`:
- `domain.pddl`: a STRIPS PDDL domain for the travelling purchase problem, with the actions drive, buy, load and unload.
- `problem.pddl`: one problem instance, with `:objects`, `:init` and `:goal`.
- `plans/plan_XX.txt`: candidate plans. Each line holds one action in the form `name(obj1, obj2, ...)`. Blank lines are ignored.

Simulate each plan from the initial state using standard STRIPS semantics. Compare all names case-insensitively.

An action line is applicable if and only if all of the following hold:
- the action name is defined in the domain;
- the number of arguments equals the number of parameters;
- every argument is an object declared in the problem's `:objects`;
- every precondition atom, after substituting parameters with arguments, holds in the current state.

Types are not checked. Applying an action first removes its delete effects (the `not` atoms) and then adds its add effects. Execution stops at the first line that is not applicable.

Write `/root/work/results.json` in this form:
```json
{"plans": {"plan_01": {"num_actions": 41, "first_failure": null, "goal_reached": true}},
 "valid_plans": ["plan_01"]}
```
- The keys of `plans` are the plan file names without `.txt`. Include one entry per plan file.
- `num_actions` (integer): the number of non-blank lines.
- `first_failure`: the 1-based index, counted among non-blank lines, of the first inapplicable line. Use `null` if every line is applicable.
- `goal_reached` (boolean): true if and only if `first_failure` is null and every goal atom holds in the final state.
- `valid_plans`: the sorted list of plan ids whose `goal_reached` is true.
