# Count shortest airport service plans

`/root/work/domain.pddl` and `/root/work/problem.pddl` describe one aircraft moving through a directed taxiway network. Read the typed objects, initial facts, and goal from the PDDL files. The `move` action follows a `connected` fact and changes the aircraft's location. The `service` action can be performed at a node with an `unserviced` fact; it replaces that fact with `serviced`. Each action costs one step. Connections are directed, and an aircraft may revisit a node.

The goal requires the aircraft to be at its specified destination and every goal service fact to hold. A state is distinguished by both the aircraft's location and the set of nodes already serviced. Count distinct action sequences, not merely distinct states: two different sequences reaching the same state are two plans. A shortest plan has the smallest possible total number of `move` and `service` actions.

Write exactly one UTF-8 JSON object to `/root/work/service_summary.json`. It must have exactly three integer fields: `min_steps`, the length of a shortest goal-reaching plan; `shortest_plans`, the number of distinct plans of that length; and `reachable_states`, the number of states reachable from the initial state by any finite sequence of applicable actions, including the initial state. Do not apply a modulus or include explanatory text.
