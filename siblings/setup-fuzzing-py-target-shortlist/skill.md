## Reference notes

Use Python’s standard-library `ast`, `pathlib`, and `csv`. This is static source analysis; do not import or execute package code. Inspect the generated `.py` files themselves, not their filenames as a proxy for contents.

- For each file in `Path("/root/work/pkg").glob("*.py")`, parse `path.read_text(encoding="utf-8")` with `ast.parse(...)`. Eligible declarations are `ast.FunctionDef` or `ast.AsyncFunctionDef` nodes **directly in** `tree.body`, with names not starting `_`. Exclude methods and nested functions. The module name is `path.stem`.
- Function parameter names are in `node.args.posonlyargs`, `args`, and `kwonlyargs`, plus `node.args.vararg` and `kwarg` when present. Each parameter node has an `.arg` string.
- For each test file, examine `ast.ImportFrom` nodes whose `module` is `pkg.<module>`. An imported symbol’s local call name is `alias.asname or alias.name`; retain the mapping to its original `<module>.<name>`. A direct call has an `ast.Call` whose `func` is an `ast.Name` matching that local name. A call through an attribute, such as `module.name(...)`, is not a directly imported-name call.
- Inspect calls within each test function separately. Use its file and source location to distinguish test functions; count a given test function **once per target**, however many qualifying calls it contains. Avoid attributing calls inside a nested function definition to its enclosing test function.

Scoring is literal and case-sensitive: `+3` **once** if the function name contains any of `parse`, `decode`, `load`, `validate`; `+2` **once** if any parameter is named `data`, `payload`, `text`, or `raw`; then `−2 × test_functions`. Sort all eligible functions by `(-score, qualname)` and take three.

Write with `open("/root/work/target_shortlist.csv", "w", encoding="utf-8", newline="")` and `csv.writer`; emit exactly the header `qualname,score,test_functions` followed by the three rows. Check the resulting header, row count, ordering, and integer fields without changing package or test files.
