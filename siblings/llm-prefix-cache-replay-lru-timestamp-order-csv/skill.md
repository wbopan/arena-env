## Reference notes

Use only Python’s standard library: `json` for JSON Lines, `csv` for output, and `collections.OrderedDict` for LRU. `hash_ids` are already block hashes; do not tokenize or hash the prompt.

- Read each nonempty trace line with `json.loads(line)`. Sort requests by `timestamp` using Python’s stable `list.sort(key=lambda r: r["timestamp"])`; equal timestamps then retain file order.
- Keep LRU keys in an `OrderedDict`, **least recently used at the head**, most recently used at the tail. Membership checks do not change recency:
  ```python
  cache = OrderedDict()

  def access(block, capacity):
      if block in cache:
          cache.move_to_end(block)
      else:
          cache[block] = None
          if len(cache) > capacity:
              cache.popitem(last=False)
  ```
- For each request, **before accessing any of its blocks**, scan `hash_ids` from index 0. `hit_blocks` is the count up to the first block absent from `cache`; do not count resident blocks beyond that first miss. Then calculate `hit_tokens = min(hit_blocks * block_size, input_length)`.
- After that scan, call `access` on **every** hash in request order, including blocks outside the hit prefix. This updates recency on resident-block accesses and evicts the LRU block when an insertion exceeds capacity.
- Write CSV with `csv.writer`, the exact specified header, and one row per sorted request. Map `prompt_tokens` to `input_length`; `output_length` does not enter these calculations. Open the output with `newline=""` to avoid extra line endings.
