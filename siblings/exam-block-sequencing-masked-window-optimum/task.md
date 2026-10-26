# Masked-window exam sequence

A registrar must assign seven exam blocks to seven labeled slots. The slot labels are not consecutive numbers: use their order in `instance.json`, not their spelling, to determine which slots are adjacent. Find the feasible schedule with the smallest defined burden.

Inputs in `/root/work` are `instance.json`, `pair_counts.csv`, and `triple_counts.csv`. The JSON lists `slot_order`, `blocks`, `large_blocks`, `early_slots`, `pair_starts`, and `triple_starts`. Each start is a zero-based index into `slot_order`. A pair start scores the block at that index followed by the block at the next index; a triple start scores the three blocks beginning there. The CSV columns are respectively `first,second,count` and `first,second,third,count`. Tuple order matters. Both tables contain every ordered tuple of distinct blocks.

Assign every block exactly once and fill every slot exactly once. Each large block must occupy an early slot. Minimize the sum of the counts at all listed pair starts plus three times the sum at all listed triple starts. There is no wraparound or cost at unlisted starts. If schedules tie, choose the lexicographically smallest sequence of block names in slot order.

Write exactly one output file, `/root/work/schedule.csv`, with header `slot,block` and one row per slot in `slot_order` order. Do not include a score or additional columns.
