# Translate Python function signatures to Scala

`/root/work/api.py` is a Python stub module. It contains top-level function definitions with full type hints and `...` bodies, plus one class. You need the equivalent Scala 2.13 method signatures for every **top-level** function. Ignore methods defined inside classes.

Write `/root/work/signatures.json`: a JSON array with one object per top-level function, in source order. Each object has exactly these keys:

- `python_name`: the original Python name, including any leading underscore.
- `scala_name`: the Scala method name.
- `signature`: the Scala signature string.

**Naming.** Strip leading underscores and convert snake_case to camelCase. The first word stays as is. Each later word gets its first character upper-cased, so `parse_v2_header` becomes `parseV2Header`. Parameter names are converted the same way.

**Visibility.** A function whose Python name starts with `_` is private.

**Types.**

| Python | Scala |
|---|---|
| `int` | `Int` |
| `float` | `Double` |
| `str` | `String` |
| `bool` | `Boolean` |
| `bytes` | `Array[Byte]` |
| `list[X]` | `List[X]` |
| `set[X]` | `Set[X]` |
| `dict[K, V]` | `Map[K, V]` |
| `tuple[A, B, ...]` | `(A, B, ...)` |
| `Optional[X]` or `X \| None` | `Option[X]` |
| return type `None` | `Unit` |

Types are applied recursively.

**Signature format.** Use exactly this shape:

`[private ]def <scalaName>(<p1>: <T1>, <p2>: <T2>): <R>`

- Parameters are separated by `, `.
- Type arguments inside `[...]` and tuple elements are separated by `, `.
- A function with no parameters is written `def name(): R`.
- Use single spaces as shown, with no trailing spaces.

Example: `def fetch_rows(row_ids: list[int], limit: int | None) -> dict[str, float]` becomes `def fetchRows(rowIds: List[Int], limit: Option[Int]): Map[String, Double]`.
