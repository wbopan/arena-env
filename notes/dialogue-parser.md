**Goal and outputs.** Write `/app/solution.py`. It must define `parse_script(text: str)`, which returns a dict `{"nodes":[...],"edges":[...]}`. When run as `python3 /app/solution.py`, it must read `/app/script.txt` and write two files:

- `/app/dialogue.json`:
  - Each node: `{"id","text","speaker","type"}`, with `type` either `"line"` or `"choice"`.
  - Each edge: `{"from","to","text"}`.
- `/app/dialogue.dot`: a Graphviz digraph.

Keep the `parse_script` import side-effect free. Put the file writing under `if __name__ == "__main__":`. Tests will import the function and call it on the script text.

**Libraries.**
- The skill describes a `dialogue_graph` module: `Graph`, `Node(id, speaker, text, type)`, `Edge(source, target, text)`, `graph.to_dict()`, `graph.validate()` (returns a list of error strings), `graph.visualize()` (needs graphviz), and `Graph.from_file`.
- Check whether it exists: `python3 -c "import dialogue_graph,inspect;print(dialogue_graph.__file__)"`.
- Do not depend on it in `solution.py`. Pure Python (`re`, `json`) is safer, and you can write the DOT text by hand, so no graphviz is needed.
- If the module exists, use `Graph.from_dict(data).validate()` as an extra check only.
- Note that the JSON edge keys are `from`/`to`, not `source`/`target`.

**Script format, from the spec.**
- A block starts with a header line `[NodeId]`. The id is the text inside the brackets. Blank lines separate blocks.
- Dialogue line `Speaker: text -> Target` produces:
  - a node with `type="line"`, `speaker="Speaker"`, `text="text"`;
  - an edge `{"from":NodeId,"to":Target,"text":""}`.
- Choice block: lines like `1. option text -> Target` produce:
  - a node with id `NodeId`, `type="choice"`, `speaker=""`, `text=""`;
  - one edge per option, `{"from":NodeId,"to":Target,"text":<option text>}`.
- The skill example uses edge text `"1. Run away"`, which keeps the number. Decide on one form and keep it consistent.
- Keep tags such as `[Lie]` and `[Attack]` inside the option text. Do not mistake them for block headers. A header is a line that matches `^\[([^\]]+)\]\s*$` exactly; an option line starts with a digit.
- Split on the last `->` (`rsplit("->",1)`) and strip both sides.
- Split speaker from text on the first `:` only, because the text may contain colons.

**Pitfalls to check in the real script.**
- Inspect before coding:
  - `wc -l /app/script.txt`
  - `grep -c '^\[' /app/script.txt`
  - `head -40 /app/script.txt`
  - `grep -v -e '->' -e '^\[' -e '^$' /app/script.txt | head`, which shows lines that have no arrow.
- Lines with no `->` are terminal. Make a line node with no outgoing edge.
- A block may contain several dialogue lines. If it does, either:
  - chain them as sub-nodes (`Id`, `Id_2`, …) with empty-text edges, the last one carrying the arrow; or
  - keep one node per block.

  Check what the file actually does first.
- A block may mix a line with choices. In that case, make the line node and have it link to a choice node such as `Id_choice`.
- `End` (or any target never defined as a block) may be referenced from many places. That is allowed for the final node only. It is safest to append `{"id":"End","text":"","speaker":"","type":"line"}` if it is referenced but not defined, so validation and reachability both pass.
- Do not deduplicate edges that genuinely differ in text.
- Preserve script order. The first node must be the first block, e.g. `GateScene`, because reachability is measured from `nodes[0]`.
- Use UTF-8 when reading and writing, and `ensure_ascii=False` in `json.dump`.

**Skeleton.**
```python
import re, json
HDR = re.compile(r'^\[([^\]]+)\]\s*$')
OPT = re.compile(r'^\d+\.\s*(.*)$')

def parse_script(text):
    nodes, edges, order, blocks, cur = [], [], [], {}, None
    for raw in text.splitlines():
        s = raw.strip()
        if not s: continue
        m = HDR.match(s)
        if m:
            cur = m.group(1).strip(); order.append(cur); blocks[cur] = []
        elif cur:
            blocks[cur].append(s)
    for bid in order:
        lines = blocks[bid]
        if lines and all(OPT.match(l) for l in lines):
            nodes.append({"id":bid,"text":"","speaker":"","type":"choice"})
            for l in lines:
                body, _, tgt = l.rpartition("->") if "->" in l else (l, "", "")
                if tgt.strip():
                    edges.append({"from":bid,"to":tgt.strip(),"text":body.strip()})
        else:
            for l in lines:  # adapt if blocks have several lines
                body, tgt = (l.rsplit("->",1)+[""])[:2] if "->" in l else (l, "")
                sp, _, tx = body.partition(":") if ":" in body else ("", "", body)
                nodes.append({"id":bid,"text":tx.strip(),"speaker":sp.strip(),"type":"line"})
                if tgt.strip(): edges.append({"from":bid,"to":tgt.strip(),"text":""})
    ids = {n["id"] for n in nodes}
    for e in edges:
        if e["to"] not in ids:
            nodes.append({"id":e["to"],"text":"","speaker":"","type":"line"}); ids.add(e["to"])
    return {"nodes":nodes,"edges":edges}
```

**DOT output.** Write it manually and escape `"` and `\` in labels.
- Use `digraph Dialogue {`.
- Choice nodes: `shape=diamond, style=filled, fillcolor=lightblue`.
- Line nodes: `shape=box, style=rounded`, with label `Speaker: text`. Truncate long text if needed.
- Edges: `"A" -> "B" [label="..."]`.
- Optionally make edges whose text contains `[` bold blue, matching the skill's styling.
- Close with `}`.

**Plan (about 8 commands).**
1. Inspect the script with the head/grep/wc commands above. Look at the line types, multi-line blocks, terminal lines and how `End` is used.
2. Check whether `dialogue_graph` is importable.
3. Write `/app/solution.py` with a heredoc, adjusting the skeleton to what you observed.
4. Run `cd /app && python3 solution.py`.
5. Verify with a one-liner. This should print 0 for missing targets, `True` for reachability, and a small duplicate count:
```
python3 -c "import json;d=json.load(open('/app/dialogue.json'));ids={n['id'] for n in d['nodes']};print(len(d['nodes']),len(d['edges']),[e for e in d['edges'] if e['to'] not in ids]);from collections import deque;a={};[a.setdefault(e['from'],[]).append(e['to']) for e in d['edges']];s={d['nodes'][0]['id']};q=deque(s)
while q:
 for t in a.get(q.popleft(),[]):
  if t not in s:s.add(t);q.append(t)
print(ids-s, len(d['nodes'])-len(ids))"
```
6. Spot-check that `GateScene` comes first, that `NameChoice` is a choice with 4 edges, and that the `[Lie]` text is preserved. Run `head -5 /app/dialogue.dot`.
7. Confirm that `python3 -c "from solution import parse_script"` writes no files.
