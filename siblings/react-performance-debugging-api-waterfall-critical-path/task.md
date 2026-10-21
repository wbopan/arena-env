# API route waterfall analysis

The file `/root/work/api_routes.json` describes the async operations run by several Next.js API route handlers. Each route has a `route` string and an `operations` list. Each operation has a `name`, a `duration_ms` (integer) and `depends_on`, which lists the names of operations in the same route whose results it needs. Every handler currently `await`s each operation one after another, in the listed order.

For each route compute:

- `sequential_ms`: the total time of the current fully sequential implementation, which is the sum of all durations.
- `optimal_ms`: the total time if every operation starts as soon as all of its dependencies have finished. Operations with no dependencies start at 0. This value is the largest earliest-finish time in the route.
- `saved_ms`: `sequential_ms - optimal_ms`.
- `speedup`: `sequential_ms / optimal_ms`, rounded to 3 decimals.
- `critical_path`: the operation names, from first to last, of the chain that determines `optimal_ms`. Build it backwards:
  1. Start at the operation with the largest earliest-finish time.
  2. Step to the dependency with the largest earliest-finish time.
  3. Repeat until you reach an operation with no dependencies.

  Break every tie by choosing the lexicographically smallest name.

Write `/root/work/waterfall_report.json` in this form:

```json
{"routes": [{"route": "/api/x", "sequential_ms": 0, "optimal_ms": 0, "saved_ms": 0, "speedup": 0.0, "critical_path": ["a", "b"]}], "total_saved_ms": 0}
```

List the routes in the same order as the input. `total_saved_ms` is the sum of `saved_ms` over all routes. All `_ms` values are integers.
