#!/bin/bash
cd /root/work
cat > /tmp/parse.py <<'EOF'
import json, re
nodes = []; edges = []; cur = None
for raw in open('script.txt', encoding='utf-8'):
    line = raw.strip()
    if not line or line.startswith('#'):
        continue
    m = re.fullmatch(r'\[([^\]]+)\]', line)
    if m:
        cur = {"id": m.group(1).strip(), "text": "", "speaker": "", "type": "line"}
        nodes.append(cur)
        continue
    body, tgt = line.rsplit('->', 1)
    body = body.strip(); tgt = tgt.strip()
    m = re.match(r'(\d+)\.\s*(.*)', body)
    if m:
        cur["type"] = "choice"
        edges.append({"from": cur["id"], "to": tgt, "text": m.group(2).strip()})
    else:
        sp, tx = body.split(':', 1)
        cur["speaker"] = sp.strip(); cur["text"] = tx.strip()
        edges.append({"from": cur["id"], "to": tgt, "text": ""})
json.dump({"start": nodes[0]["id"], "nodes": nodes, "edges": edges}, open('dialogue.json', 'w'), indent=2)
EOF
python3 /tmp/parse.py
