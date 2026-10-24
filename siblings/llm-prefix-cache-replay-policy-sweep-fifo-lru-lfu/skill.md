## Reference notes

Use Python standard-library `json` and `collections.OrderedDict`; no cache library is needed. Read `config.json` with `json.load`, and parse `trace.jsonl` **one JSON object per nonempty line** with `json.loads`. `hash_ids` are already block hashes in prompt order; do not re-hash them. Arrival order is the file order (`timestamp` does not require sorting). `output_length` does not enter the requested metrics.

For **each policy × capacity**, start with an empty cache and replay all requests. Keep `total_requests` and `total_prompt_tokens = sum(input_length)` common to all replays.

```python
# Before changing cache state for a request:
k = 0
for h in request["hash_ids"]:
    if h not in resident:
        break
    k += 1
hit_tokens += min(k * block_size, request["input_length"])

# Only afterward, access EVERY hash in order, including hashes past
# the first prefix miss.
```

A later resident hash cannot contribute hit tokens if an earlier hash missed. Evictions caused while processing a request cannot change that request’s already-measured prefix hit.

- **FIFO:** `OrderedDict` head = earliest *admitted* resident block. A resident access does nothing. Evict with `popitem(last=False)`; append new blocks at the tail.
- **LRU:** `OrderedDict` head = least recently accessed block. On resident access call `cache.move_to_end(h)`. Evict with `popitem(last=False)`; append new blocks at the tail.
- **LFU:** Store each resident block’s frequency and a monotonically increasing **admission ordinal**. Increment frequency on every resident access; new admissions start at frequency `1`. Evict the block minimizing `(frequency, -admission_ordinal)`: the task’s tie-break selects the **most recently admitted** block among those with lowest frequency. Re-admission after eviction gets fresh state and a new ordinal. Do not use the skill document’s older-admission LFU tie-break here.

On a miss at full capacity, evict **before** admission and increment `evictions` once. Hits never evict. `final_cache_blocks` is the number of resident hashes after the replay (at most the capacity). If a capacity is zero, nothing can be admitted or evicted.

Write one JSON object to `/root/work/policy_comparison.json` with `results[policy][str(capacity)]`. For each entry, compute `hit_rate = round(hit_tokens / total_prompt_tokens, 6)` (handle a zero denominator without dividing). Check the output is valid JSON and that each reported hit-token count is between zero and `total_prompt_tokens`.
