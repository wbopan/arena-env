## Reference notes

Use Python’s standard library; the skill document’s `load_problem`, `generate_plan`, and `validate` are wrapper names, not guaranteed installed commands. Inspect the two small PDDL files first to get the **actual** action parameter order, preconditions, effects, objects, initial facts, and goal literals:

```sh
sed -n '1,220p' /root/work/domain.pddl
sed -n '1,220p' /root/work/problem.pddl
```

PDDL comments begin with `;`. If parsing in Python, remove comments before tokenizing; preserve the spelling of names used in the files:

```python
import re
text = re.sub(r";[^\n]*", "", text)
tokens = re.findall(r"\(|\)|[^\s()]+", text)
```

Parentheses are nested: do not split an action or goal at the first `)`. Read each `:action`’s `:parameters`, `:precondition`, and `:effect`; read `:init` and `:goal` from the problem. In particular, check what `buy` establishes before `load`, and what `unload` establishes for the goal—stock alone is not delivery.

Treat each road fact as a **directed** edge. For routes, breadth-first search with `collections.deque` can find a path from the truck’s current location to a market and from that market back to the depot. Do not add reverse edges unless they occur in `:init`. Plan one carried good at a time; apply every action’s effects to a tracked state before choosing the next action.

Before writing the file, replay the proposed actions against their grounded preconditions and effects, then check **every** goal literal. Write only lines such as `action(argument1, argument2)` to `/root/work/delivery.plan`, using the domain’s exact argument order and input names. No parentheses around whole lines, comments, headings, or blank lines.
