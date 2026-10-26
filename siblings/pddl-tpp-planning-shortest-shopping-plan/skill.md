## Reference notes

Use Python’s standard library (`re`, `collections.deque`, `json`). The skill document describes `unified_planning` utilities, but does not establish that they are installed or that their default planner finds a *shortest* plan. For this task, breadth-first search over reachable states gives the minimum number of actions.

- Inspect the domain’s `:action` preconditions and effects and the problem’s `:init` and `:goal` before coding. Do not assume the argument order of `road` or `available`; use their declared predicates and the action definitions.
- PDDL is case-insensitive, may span lines, and uses `;` for comments. Tokenize parentheses rather than parsing facts line by line:
  ```python
  text = re.sub(r";[^\n]*", "", path.read_text().lower())
  tokens = re.findall(r"\(|\)|[^\s()]+", text)
  ```
  Parse balanced parentheses into nested lists, then select `:init`, `:goal`, and relevant action definitions. Typed object declarations use `- type`; the hyphen and type name are not objects.
- With the stated action behavior, a compact search state is `(truck_location, owned_goods_mask)`. Generate one successor per applicable **directed** drive and one per applicable buy of a not-yet-owned goal good. Buying adds ownership; it does not replace previously owned goods. Do not add a return-to-depot requirement. Check the domain for any additional preconditions or effects before using this state representation.
- BFS: initialize the state from `:init`, enqueue it, mark states visited **when enqueued**, and retain `(previous_state, grounded_action_string)` for each discovered state. Stop when the owned mask satisfies the `:goal`. Because every action costs one step, reconstructing predecessors from the first goal state yields a shortest plan. Distances, prices, and road lengths do not enter the search.
- Write exactly the requested JSON fields, with `minimum_steps = len(actions)`, using `json.dump(...)`. Preserve the problem’s object names in strings formatted `drive(truck, from, to)` and `buy(truck, good, market)`. Recheck the reconstructed sequence against the parsed preconditions, effects, and goal.
