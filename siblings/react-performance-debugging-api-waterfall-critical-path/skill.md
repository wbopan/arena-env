## Reference notes

Use Python’s standard-library `json`; no browser or Next.js tooling is needed. The relevant waterfall principle is that independent operations can run concurrently, while an operation must wait for **all** its dependencies.

- Inspect the JSON structure briefly, then load it with `json.load()`. Keep route order by iterating the input list directly.
- For each route, index operations by `name`. Define the earliest finish time:
  `finish(name) = duration_ms(name) + max((finish(dep) for dep in depends_on), default=0)`.
  Memoized recursion or a topological traversal handles dependencies even if they are not listed before their consumers.
- The sequential duration is the sum of every operation’s `duration_ms`; the optimal duration is the maximum `finish` across operations.
- To recover the critical path, select an operation by `min(names, key=lambda n: (-finish(n), n))`. At each step, apply the same selection to its dependencies, then reverse the collected names. This implements the lexicographically smallest-name tie rule **at every step**.
- Compute the requested difference and ratio from those durations; round only `speedup` to three decimal places. Keep durations as Python integers. Handle a zero optimal duration explicitly if the input permits one.

Write one JSON object using `json.dump(report, file)` to the requested output path. After running the script, reopen the output with `json.load()` and check its route count, route order, field types, and summed savings.
