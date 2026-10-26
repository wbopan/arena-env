## Reference notes

Use Python’s standard library. The skill document describes `unified_planning` helpers, but that library is not among the available libraries; a small PDDL S-expression reader plus breadth-first search is sufficient.

- PDDL is parenthesized and case-insensitive. Strip `;` comments through the end of each line, tokenize `(`, `)`, and other non-whitespace strings, then recursively parse lists. Inspect both files before assuming predicate argument order or object types.
- In `:objects`, a group such as `a b - node` assigns **both** preceding names that type. Read `:init` facts and the (possibly `(and ...)`-wrapped) `:goal`. Preserve the direction of each `(connected source target)` fact.
- Model a state as `(location, serviced_mask)`. Assign bits to nodes whose service status can change; initialize the mask from initial `serviced` facts. A `service` transition is available where the action’s preconditions hold (notably `unserviced`) and sets that node’s bit. A `move` transition follows one directed connection. Each transition costs one, and revisits are allowed.
- Breadth-first search computes minimum distances and **counts action sequences**. For a successor `v` of `u`, first discovery sets `dist[v] = dist[u] + 1` and `ways[v] = ways[u]`; another transition at that same distance adds `ways[u]` to `ways[v]`. Do not deduplicate transitions merely because they reach the same state. Continue exploring after finding a goal to determine all reachable states.
- A goal state has the required destination and every required `serviced` fact. `min_steps` is the least goal-state distance; `shortest_plans` sums `ways` over goal states at that distance. `reachable_states` is the number of discovered states, including the initial state. Python integers need no modulus.

```python
from collections import deque
import json

# After parsing facts and constructing the initial state and transitions:
dist = {start: 0}
ways = {start: 1}
queue = deque([start])
while queue:
    state = queue.popleft()
    for nxt in successors(state):  # one applicable action per yielded transition
        candidate = dist[state] + 1
        if nxt not in dist:
            dist[nxt] = candidate
            ways[nxt] = ways[state]
            queue.append(nxt)
        elif dist[nxt] == candidate:
            ways[nxt] += ways[state]

# Select the minimum-distance goal states and aggregate their ways.
# Write one object, with exactly the three requested integer fields.
with open("/root/work/service_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f)
```

Inspect the files cheaply, write one script, run it, then check that the output is valid JSON with exactly the requested fields.
