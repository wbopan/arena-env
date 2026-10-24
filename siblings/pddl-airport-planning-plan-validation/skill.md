## Reference notes

Use Python’s standard library (`pathlib`, `re`, `json`); no planner is needed. Inspect the domain’s action definitions and the problem’s object, init, and goal sections before writing the simulator. The skill document’s `load_problem` and `validate` are helper names, not standard-library APIs; whole-plan validation alone does not provide the required first failing step or goal count.

**PDDL parsing:** Strip `;` comments to end of line, lowercase names, tokenize parentheses separately, and parse nested S-expressions rather than splitting on whitespace. Typed declarations group names before each `- type` (for example, `a b - aircraft` assigns both names that type). Read each action’s `:parameters`, `:precondition`, and `:effect`; read the problem’s `:objects`, `:init`, and conjunctive `:goal`. Represent a ground atom as a tuple such as `("at", "plane", "node")`, and the state as a set of tuples.

**Plan lines:** Ignore blank lines and lines *starting* with `;`. Number only the remaining lines, from 1. Parse the entire line as `name(arg1, arg2, ...)`; reject malformed syntax, including empty arguments. Match names case-insensitively. Before checking preconditions, check that the action exists, arity matches, and every argument is a declared object of **exactly** the parameter’s declared type.

**Sequential STRIPS:** Substitute arguments for parameters to ground the action’s atoms. A positive precondition must be in the current state; a negative precondition, if present, must be absent. On success, update the state with `state.difference_update(deletes)` **then** `state.update(adds)`. On either step failure, stop without changing that step’s pre-state.

For each plan, count goal atoms present in the **last reached state**. If no step fails but a goal is missing, use `reason: "goal"` and `failed_step: null`; if all goals hold, set `valid: true` and both failure fields to null. Write a JSON object keyed by each plan’s filename to `/root/work/validation.json`. After running the script, briefly inspect the JSON for all expected filenames and correctly shaped records.
