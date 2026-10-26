## Reference notes

Use Python’s standard library (`re`, `csv`); no planner is needed. This task traces the supplied actions, not a newly generated plan or goal satisfaction.

- In PDDL, `;` starts a line comment. Read `problem.pddl`, remove comments, and isolate the parenthesized `:init` section (track parentheses to find its end). Extract its `(at aircraft location)` fact and `(connected origin destination)` facts. Store connections as **ordered** `(origin, destination)` pairs; never add reverse edges.
- Read `candidate.plan` in order. Preserve each examined line’s action text apart from its line ending (`line.rstrip('\r\n')`); use a stripped copy only for parsing `move(aircraft, origin, destination)`.
- For each move, check both `current_location == origin` and `(origin, destination) in connections`. Update the location only when both hold. Record the action either way, then stop immediately if invalid.
- Write `/root/work/trace.csv` with `csv.writer` and `open(..., 'w', encoding='utf-8', newline='')`. Start with `['step', 'action', 'valid', 'location']` and `[0, 'INIT', 'true', initial_location]`; use lowercase string values for subsequent validity. `csv.writer` handles quoting action text containing commas.
