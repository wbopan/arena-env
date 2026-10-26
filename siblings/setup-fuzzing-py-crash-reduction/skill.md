## Reference notes

Use Python’s standard library; this is a **subsequence optimization**, not a fuzzing run. Retained bytes must remain in original order.

```python
from pathlib import Path
import json

source = Path("/root/work/crash.bin").read_bytes()
rule = json.loads(Path("/root/work/crash_rule.json").read_text(encoding="utf-8"))
magic = bytes.fromhex(rule["magic_hex"])  # should be exactly two bytes
remainder = rule["remainder"]
```

A compact exact approach is dynamic programming over the source bytes. For each processed prefix, keep the best candidate for each state:

`(matched_magic_bytes, byte_sum_mod_11, has_zero_after_magic, min(length, 4))`

Here `matched_magic_bytes` is 0, 1, or 2. For every source position, branch into **delete** and **retain**. Retention is allowed during the first two output bytes only when the byte matches the corresponding byte of `magic`; afterward, update the zero flag if the retained byte is `0`. Update the residue with `(old_residue + byte) % 11`. Track the actual output bytes and ascending original indices with each candidate.

For candidates in the *same state*, keep the minimum under:

```python
(len(candidate_bytes), candidate_bytes, candidate_indices)
```

This order implements all three tie-breaks. The capped length in the state is essential: lengths 0–3 must remain distinguishable so a too-short result cannot displace a valid length-4 result. At the end, consider only states with two matched magic bytes, capped length 4, a post-magic zero, and residue equal to `remainder`; select by the same ordering.

Check the selected result before writing: its length is at least 4, it starts with `magic`, `0 in result[2:]`, its sum modulo 11 matches, and reconstructing it from `source` at the retained indices gives identical bytes. Write **only** `/root/work/minimized.json`:

```python
payload = {
    "minimized_hex": result.hex(),  # lowercase
    "length": len(result),
    "retained_indices": list(indices),
}
Path("/root/work/minimized.json").write_text(
    json.dumps(payload), encoding="utf-8"
)
```

Read inputs as bytes/JSON respectively; do not decode the binary input as text or modify either input file.
