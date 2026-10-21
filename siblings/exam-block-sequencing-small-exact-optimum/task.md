# Optimal sequence for a small exam-block instance

Assign 8 exam blocks to 8 time slots so that the total student burden is minimized.

Inputs in /root/work:
- `instance.json` contains these fields:
  - `slot_order`: slot labels in chronological order. This list defines "next slot".
  - `blocks`.
  - `large_blocks` and `early_slots`.
  - `b2b_start` and `triple_start`: lists of start slots.
  - `weights`: an object with keys `b2b` and `triple`.
- `pair_counts.csv` has columns `block_i,block_j,count`. Each row is an ordered pair. Missing pairs count 0.
- `triplet_counts.csv` has columns `block_i,block_j,block_k,count`. Each row is an ordered triple. Missing triples count 0.

Feasibility rules:
- Each block is assigned to exactly one slot.
- Each slot receives exactly one block.
- Every block in `large_blocks` must be placed in a slot listed in `early_slots`.

Objective (minimize). Let b(s) be the block in slot s, and let next(s) follow `slot_order`.

  weights.b2b * sum over s in b2b_start of pair(b(s), b(next(s)))
  + weights.triple * sum over s in triple_start of triple(b(s), b(next(s)), b(next(next(s))))

All keys are ordered tuples in schedule order. Do not sort or symmetrize them.

Output: write `/root/work/schedule.csv` with the header `slot,block` and one row per slot (8 rows). Use slot labels and block ids exactly as they appear in `instance.json`. The schedule must be feasible and must attain the minimum possible objective value. If several schedules are optimal, any one of them is acceptable.
