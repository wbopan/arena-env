## Reference notes

Use Python’s standard library for this small, unit-cost planning problem. The skill document describes `load_problem`, `generate_plan`, and `save_plan` as planning helpers, but does not establish them as installed Python imports. Breadth-first search (BFS) over grounded states guarantees a shortest **sequential** plan when every action costs one.

- Read **both** PDDL files. Strip `;`-to-end-of-line comments before parsing. PDDL is nested S-expression syntax: a flat regex can extract tokens, but should not be used to match whole nested sections. Tokenize with `re.findall(r'\(|\)|[^\s()]+', text)` and parse balanced parentheses.
- Extract aircraft and node object names, initial `at`, `clear`, `edge`, and `target` facts, and the conjunctive goal. Preserve the problem’s object spelling in the output. Do not infer an edge’s reverse.
- Represent a state with each aircraft’s location or parked status **and** the set of clear nodes. This keeps the search faithful to action preconditions and effects. Check the actual domain for any additional conditions or effects.

For each unparked aircraft at `origin`, generate `move` successors only for declared `(edge origin destination)` facts whose destination is clear. Update its location; add `origin` to clear and remove `destination`. Generate `park` only when its current node matches its `target` fact; remove its location, mark it parked, and add that node to clear. A parked aircraft has no move successors.

```python
from collections import deque

queue = deque([initial_state])
parent = {initial_state: None}  # successor -> (preceding_state, grounded_action)

while queue:
    state = queue.popleft()
    if goal_holds(state):
        break
    for action, successor in legal_successors(state):
        if successor not in parent:
            parent[successor] = (state, action)
            queue.append(successor)
```

Reconstruct actions by following `parent` backward from the goal, then reverse them. Before writing, replay them from the parsed initial state, checking every precondition and effect and the final conjunctive goal. Write only `/root/work/parking.plan` as UTF-8, with one `move(aircraft, origin, destination)` or `park(aircraft, node)` per line—no numbering, comments, or blank lines.
