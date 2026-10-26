## Reference notes

Use Python’s standard-library `json`, `csv`, `ipaddress`, and `collections`; no PCAP tooling or Suricata rerun is needed. EVE JSON is **newline-delimited JSON**: parse each nonempty line separately, not the whole file as one JSON document.

```python
import json
from collections import defaultdict
from ipaddress import IPv4Address

with open("/root/work/eve.json", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            event = json.loads(line)
            # Process event by event["event_type"].
```

- Join HTTP and alert events by the **pair** `(flow_id, tx_id)`, not either ID alone. Events can arrive in any order, so collect matching alert keys and HTTP records before reconciling them.
- An alert qualifies by `event["alert"]["signature_id"] == 1000001`; other signatures do not. Store qualifying keys in a `set` so repeated alerts cannot multiply a transaction.
- Apply method, URL, and mode conditions to the **HTTP record’s** `http` object. Take the source IP and `request_body_len` from that same HTTP record. Count each qualifying transaction once; sum its body length as bytes, without conversion.
- Sort source strings numerically with `key=IPv4Address`, not lexicographically.

Write CSV using `csv.writer` with `newline=""`:

```python
with open("/root/work/source_totals.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["src_ip", "transactions", "body_bytes"])
    # Write one row per counted source, in IPv4Address order.
```

A quick check can read back the CSV header and rows and confirm that numeric fields are decimal integers and addresses are in numeric order.
