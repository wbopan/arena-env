# Exam schedule metric audit

A registrar has a fixed final-exam schedule that assigns 12 exam blocks to 12 slots. Recompute its student-burden metrics from the data.

Inputs in /root/work:
- `instance.json` contains these fields:
  - `slot_order`: the slot labels in chronological order. This list alone defines the "next slot".
  - `blocks`.
  - Start-slot lists `eve_morn_start`, `other_b2b_start`, `triple_day_start`, `triple_24_start` and `four_start`.
- `pair_counts.csv` has columns `block_i,block_j,count`. Each row is an ordered pair. Missing pairs count 0.
- `triplet_counts.csv` has columns `block_i,block_j,block_k,count`. Each row is an ordered triple. Missing triples count 0.
- `schedule.csv` has columns `slot,block`. The rows are in arbitrary order.

Let b(s) be the block placed in slot s. Let s+1, s+2 and s+3 be the slots that follow s in `slot_order`. Compute:
- eve_morn_b2b_count = sum over s in eve_morn_start of pair(b(s), b(s+1))
- other_b2b_count = the same sum over other_b2b_start
- same_day_triple_count = sum over s in triple_day_start of triple(b(s), b(s+1), b(s+2))
- cross_day_triple_count = the same sum over triple_24_start
- z_three_in_four_count = sum over s in four_start of triple(b(s), b(s+1), b(s+3)) + triple(b(s), b(s+2), b(s+3))
- objective = 1*eve_morn_b2b_count + 1*other_b2b_count + 10*same_day_triple_count + 10*cross_day_triple_count + 5*z_three_in_four_count

All pair and triple keys are ordered. Do not sort or symmetrize them.

Output: write `/root/work/metrics.json`. It must be a JSON object with these integer fields: `objective`, `eve_morn_b2b_count`, `other_b2b_count`, `same_day_triple_count`, `cross_day_triple_count`, `z_three_in_four_count`.
