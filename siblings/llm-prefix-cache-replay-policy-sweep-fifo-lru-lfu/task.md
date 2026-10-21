Compare three eviction policies for a block-level KV prefix cache. Replay `/root/work/trace.jsonl` once for every combination of policy and capacity.

**Inputs**

- Each trace line has `timestamp`, `input_length` (prompt tokens), `output_length` and `hash_ids` (block hashes in prompt order). Lines are already in arrival order.
- `/root/work/config.json` gives `block_size`, `policies` (a list from FIFO, LRU, LFU) and `capacities` (a list of block counts).
- Every replay starts from an empty cache.

**Processing each request**

1. When the request arrives, let k be the length of the longest run of resident blocks starting at `hash_ids[0]`. The request's hit tokens are `min(k*block_size, input_length)`.
2. Then access every block of `hash_ids` in order.

**Access rules**

- Resident block:
  - LRU: the block becomes most-recently-used.
  - LFU: increment its frequency.
  - FIFO: nothing changes.
- Non-resident block:
  - If the cache is full, first evict one block. FIFO evicts the earliest admitted block. LRU evicts the least recently used block. LFU evicts the lowest frequency, breaking ties by the earliest (most recent) admission time.
  - Then admit the new block. Under LFU it is admitted with frequency 1.
  - An evicted block loses all state.

**Output**

Write `/root/work/policy_comparison.json` with these fields:

- `total_requests` (int)
- `total_prompt_tokens` (int)
- `results`: a mapping `results[policy][str(capacity)]`, where each entry is an object with:
  - `hit_tokens` (int)
  - `hit_rate`: `hit_tokens / total_prompt_tokens`, rounded to 6 decimals
  - `evictions` (int count)
  - `final_cache_blocks` (resident blocks at the end)
