## Reference notes

Use Python’s standard-library `json` and `re`; this input is already a JSONL export of complete requests, so PCAP, tshark, and Suricata tools are unnecessary.

```python
import json
import re

with open("/root/work/requests.jsonl", encoding="utf-8") as f:
    records = (json.loads(line) for line in f if line.strip())
```

For each `record["request"]`, split **once** at the first `"\r\n\r\n"` to separate the request line and headers from the body. Parse the method and request target from the request line; require the target to equal the specified path, rather than accepting a longer path or a query string. Parse header lines at their first `:`, compare names with `.lower()`, and compare the required header value after `.strip()`.

Inspect parameters **only in the body**. Split it on `&`, then split each parameter at its first `=` so additional `=` characters remain in the value. Names and values are case-sensitive; don’t match substrings of another parameter name. For candidate values, `re.fullmatch()` enforces the entire value:

```python
re.fullmatch(r"[A-Za-z0-9+/=]{80,}", blob_value)
re.fullmatch(r"[0-9A-Fa-f]{64}", sig_value)
```

The blob requirement is an alphabet-and-length check, not a Base64 decoding requirement. Preserve the signature’s original case when taking its first eight characters. Sort result objects by integer `id`, and write a JSON array (including `[]` when empty) with `json.dump()`.
