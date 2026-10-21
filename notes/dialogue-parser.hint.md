1. Inspect `/app/script.txt` cheaply (`head -40`, `grep -c '^\['`, lines without `->`) and check whether `dialogue_graph` imports. Use it only for optional `validate()`.
2. Write `/app/solution.py` in pure `re`/`json`. Its `parse_script(text)` maps `[Id]` headers to nodes: `Speaker: text -> T` becomes a line node plus an edge with text `""`; numbered options become a choice node plus one edge per option carrying the option text.
3. Keep `[Lie]`-style tags in the option text, keep the first block first, and append `End` (or any undefined target) as a node.
4. Under `__main__`, write `/app/dialogue.json` (`{"nodes":[{id,text,speaker,type}],"edges":[{from,to,text}]}`) and a hand-written `/app/dialogue.dot` digraph.
5. Run it, then verify with a one-liner that no edge targets are missing and every node is reachable from `nodes[0]`.
