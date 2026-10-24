## Reference notes

Use Python’s standard library (`pathlib`, `re`, `json`). The skill’s `validate(problem, plan)` checks whether a *whole* plan solves a problem; it does not supply the required first failing action index. A small STRIPS simulator is better suited to this task.

**Parse PDDL as S-expressions**, not with a regex that tries to match nested parentheses. Strip `;` comments, lowercase tokens for case-insensitive matching, and tokenize parentheses separately:

```python
text = re.sub(r";[^\n]*", "", path.read_text()).lower()
tokens = re.findall(r"\(|\)|[^\s()]+", text)
```

A recursive parser can represent each parenthesized expression as a Python list. In the resulting top-level `(define ...)` list, locate sections by their first element: domain `:action` sections; problem `:objects`, `:init`, and `:goal`. Within an action, `:parameters`, `:precondition`, and `:effect` are followed by their respective expressions.

**Represent atoms as tuples** such as `("at", "truck", "market")`; represent the state as a set of atoms. An `(and ...)` expression contains multiple atoms; a lone atom is also valid. For effects, separate `(not (predicate ...))` into the delete set and positive atoms into the add set. Substitute parameter tokens (including their leading `?`) with the corresponding plan arguments in predicate positions.

Parameter and object declarations may contain type annotations, e.g. `?x - location` or `a b - location`. Types are **not** applicability constraints here: retain the names before `-`, and skip the `-` and its type expression when extracting parameter/object names. Unannotated names also count.

For each plan, count **all non-blank lines before simulation**, including lines after any failure. Parse each line with a full-line match of `name(...)`, splitting its comma-separated arguments and trimming whitespace. A malformed line is inapplicable. Process lines in order, using a fresh copy of the initial state per plan:

```python
# After action-name, arity, declared-object, and precondition checks:
state.difference_update(ground_delete_effects)
state.update(ground_add_effects)
```

Stop at the first inapplicable non-blank line; its index starts at 1. Only if no line fails, check that every goal atom belongs to the final state. Read `plans/plan_*.txt` with `Path.glob`, use each file’s `.stem` as its ID, sort `valid_plans`, and write JSON with `json.dump`.
