## Reference notes

Use Python’s standard-library `ast` to read the stub without importing it. `ast.parse(source).body` preserves source order; select only nodes that are **direct children** of the module and are `ast.FunctionDef`. Do not walk recursively: that would include class methods.

```python
from pathlib import Path
import ast
import json

tree = ast.parse(Path("/root/work/api.py").read_text())
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
```

For each function, `node.name` is its original name, `node.args.args` holds ordinary positional parameters, and `node.returns` holds its return annotation. Each parameter’s `.arg` is its name and `.annotation` is its type AST. Ignore `...` bodies.

**Naming:** private iff the original function name starts with `_`. For Scala names, remove *all* leading underscores with `lstrip("_")`, split on `_`, retain the first word, and uppercase only the first character of each subsequent word. Apply the same conversion to parameter names. The `python_name` JSON field retains the original name.

**Recursive annotation mapping:**

| AST form | Interpretation |
|---|---|
| `ast.Name(id=...)` | `int → Int`, `float → Double`, `str → String`, `bool → Boolean`, `bytes → Array[Byte]` |
| `ast.Subscript` with base `list`, `set`, `dict`, or `tuple` | `List[X]`, `Set[X]`, `Map[K, V]`, or `(A, B, ...)` |
| `ast.Subscript` with base `Optional` | `Option[X]` |
| `ast.BinOp(op=ast.BitOr)` with one side `None` | `Option[X]`, where `X` is the other side |
| return annotation `None` | `Unit` |

For multi-argument subscripts such as `dict[K, V]` and `tuple[A, B]`, `.slice` is an `ast.Tuple`; its `.elts` contain the arguments. Single-argument subscripts use `.slice` directly. Apply the mapping recursively so nested collections and optionals work. In annotations, `None` can appear as `ast.Constant(value=None)`.

Build each signature as `("private " if private else "") + "def " + scala_name + "(" + ", ".join(parameters) + "): " + return_type`; each parameter is `camelName: ScalaType`. Keep `()` for zero parameters. Use `json.dumps(records, indent=2)` and write the resulting array to `/root/work/signatures.json`; each record needs exactly `python_name`, `scala_name`, and `signature`.

A short workflow: inspect the stub once, implement the AST conversion in one Python script, run it, then inspect the JSON for source order, excluded class methods, nested type formatting, and exact spacing.
