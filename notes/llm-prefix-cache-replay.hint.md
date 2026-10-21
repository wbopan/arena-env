1. Run `cat /root/config.json` and `head -c 400 /root/trace.jsonl`; replay with plain Python and OrderedDicts.
2. For each request, first count the longest resident prefix k (resident means S∪M, ghost excluded), then hit = min(k*block_size, input_length). Then access EVERY hash with S3FIFO.
3. S3FIFO setup: small_cap = round(cap*ratio), main = ghost = cap - small. Promote S→M if freq≥1, keeping freq. M uses second-chance eviction (decrement, requeue at tail). A ghost hit goes to M with freq 0. Clamp freq at max_freq.
4. Write /root/report.json with the totals, the rate, final_cache_blocks = |S|+|M|, and per_request entries {idx, prompt_tokens, hit_tokens}. Then check that the sums and the rate are consistent.
