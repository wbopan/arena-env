# Audit a dialogue graph

The input `/root/work/dialogue.json` is a dialogue graph of the form
`{"nodes":[{"id","text","speaker","type"}], "edges":[{"from","to","text"}]}`.

Conventions:
- The first entry of `nodes` is the start node.
- The target id `End` is the terminal marker. It never appears in `nodes`.
- An edge whose `to` is neither a node id nor `End` is a broken link.
- Edges are directed. Parallel edges (same `from` and same `to`) are distinct transitions.
- The graph is guaranteed to be acyclic.

Compute the following and write them to `/root/work/report.json` as a single JSON object:

- `start`: the id of the start node.
- `reachable_count`: the number of nodes reachable from the start node, including the start node itself. Traversal follows edges only into existing nodes.
- `unreachable`: the ids of nodes that are not reachable, sorted ascending.
- `missing_targets`: the distinct broken-link target ids, sorted ascending.
- `dead_ends`: the ids of all nodes with zero outgoing edges, whether reachable or not, sorted ascending.
- `paths_to_end`: the number of distinct edge sequences that lead from the start node to `End`. Count each parallel edge separately. Paths through broken links do not count.
- `shortest_to_end`: the minimum number of edges on any path from the start node to `End`. Use -1 if `End` cannot be reached.

All list values are JSON arrays of strings. All counts are integers.
