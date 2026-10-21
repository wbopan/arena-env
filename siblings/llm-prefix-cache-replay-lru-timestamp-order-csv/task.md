Replay the LLM inference request trace `/root/work/trace.jsonl` through a block-level KV prefix cache that uses **LRU** eviction. Report per-request prefix-hit statistics.

Each line of the trace is one request. Its fields are `request_id` (string), `timestamp` (int), `input_length` (prompt tokens), `output_length`, and `hash_ids`, which lists the prompt's block hashes in order. The lines are NOT stored in arrival order. Process requests in ascending `timestamp`. Requests with equal timestamps are processed in the order their lines appear in the file.

`/root/work/config.json` gives `block_size` (tokens per block) and `cache_capacity_blocks` (maximum resident blocks). The cache starts empty.

For each request:

1. When the request arrives, compute `hit_blocks`. This is the largest k such that the first k entries of `hash_ids` are all resident. The count starts at index 0 and stops at the first non-resident block.
2. Compute `hit_tokens = min(hit_blocks * block_size, input_length)`.
3. Access every block of `hash_ids` in order, using LRU rules:
   - A resident block becomes the most-recently-used block.
   - A non-resident block is inserted as the most-recently-used block.
   - If the cache now holds more than `cache_capacity_blocks` blocks, the least-recently-used block is evicted.

Write `/root/work/hits.csv` with this exact header:

`request_id,timestamp,prompt_tokens,hit_blocks,hit_tokens`

Write one row per request, in processing order. `prompt_tokens` equals `input_length`. All numeric values are integers.
