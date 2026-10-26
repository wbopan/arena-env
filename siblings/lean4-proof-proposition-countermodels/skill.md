## Reference notes

The Lean skill documents do not apply: these files contain JSON ASTs, not Lean syntax. Use Python’s standard-library `json` and `itertools`; no theorem prover or numerical library is needed.

- Read with `json.load(open("/root/work/claims.json"))`; write with `json.dump(result, open("/root/work/countermodels.json", "w"))`. Python `True`, `False`, and `None` become JSON `true`, `false`, and `null`.
- Evaluate each AST recursively. A `var` node looks up its name in the assignment; `not` negates its child. For binary nodes, `and` is conjunction, `or` is disjunction, and `imp` evaluates as `(not left) or right`. The operands are the two elements of the node’s list.
- `itertools.product((False, True), repeat=4)` enumerates assignments in the required lexicographic order when paired with `("a", "b", "c", "d")`. Build each assignment with `dict(zip(names, values))`, retaining all four names even if unused.
- For each claim in input order, take the **first** assignment on which its formula is false. If none exists, it is valid and its counterexample is `None`. Emit only the three requested keys per entry.

A short workflow: inspect the JSON structure without printing the entire file, write one Python script with a recursive evaluator, run it, then inspect the output’s entry count, key sets, and boolean/null types.
