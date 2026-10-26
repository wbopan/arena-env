# Recover directed adjacency counts

A registrar recorded the adjacency burden of several complete exam schedules, but four entries were omitted from the directed pair-count table. Recover those entries from the observations. This is a data-reconciliation task; do not rearrange or optimize the observed schedules.

The inputs in `/root/work` are `instance.json`, `pair_counts.csv`, `missing_pairs.csv`, and `observations.csv`. The JSON field `slot_order` gives the chronological order of six slots, and `blocks` lists their block names. `pair_counts.csv` has columns `first,second,count` and supplies every ordered pair of distinct blocks except those named in `missing_pairs.csv`. That latter file has columns `first,second`. A pair and its reverse are different entries.

Each row of `observations.csv` has one column per slot, named exactly as in `slot_order`, followed by `total`. Its slot columns give a complete schedule; `total` is the sum of the five directed counts for adjacent blocks in that schedule. No pair crosses from the final slot back to the first. The four missing counts are integers from 1 through 6 inclusive, and the observations identify one solution in that range.

Write exactly `/root/work/inferred_pairs.csv`. Use the header `first,second,count`, with four rows in the same order as `missing_pairs.csv`. Counts must be unrounded decimal integers. Include no other rows or columns.
