## Reference notes

Use Python’s standard-library `json` to read and write the supplied schema. The skill’s `dialogue_graph` API uses `source`/`target` for edges, while this file uses `"from"`/`"to"`; direct dictionary processing avoids a conversion. Keep edges as a **list**, not a set: parallel edges count as separate transitions.

```python
import json

with open("/root/work/dialogue.json", encoding="utf-8") as f:
    data = json.load(f)

nodes = data["nodes"]
edges = data["edges"]
start = nodes[0]["id"]
node_ids = {node["id"] for node in nodes}
```

- Reachability: traverse from `start`, following only edges whose `"to"` is in `node_ids`. Count visited node ids; sort the remaining ids for `unreachable`.
- Broken links: collect distinct `"to"` values outside `node_ids` **except `"End"`**, then sort.
- Dead ends: count *all* outgoing edges for each node, including edges to `"End"` or broken targets. A node with count zero is a dead end, whether reachable or not.
- Path counts: because the graph is acyclic, use topological-order dynamic programming or memoized recursion over valid node-to-node edges. Each edge contributes separately; an edge to `"End"` contributes one completed path, while a broken link contributes none.
- Shortest distance: an edge directly to `"End"` has length 1; otherwise add 1 to a successor’s distance when that successor can reach `"End"`. Use `-1` if no such path exists. A breadth-first traversal that treats `"End"` as a terminal is another option.
- Write one JSON object with `json.dump(...)`. Keep counts as integers and sorted id lists as arrays of strings.
