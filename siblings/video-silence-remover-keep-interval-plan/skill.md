## Reference notes

Use Python’s standard-library `json`; no audio or video processing is needed. The detector files have `segments` arrays, but their optional `duration` fields and reported totals are not authoritative for this plan. The segment-combiner documents only sorting, not clipping or unioning, so calculate those explicitly.

1. Inspect `recording.json` for the duration field, then load it and both detector files with `json.load(open(path))`.
2. For each proposed `[start, end)`, clip with `start = max(0, start)` and `end = min(duration_seconds, end)`; retain only `start < end`.
3. Sort the retained pairs. Build their union by extending the last merged interval whenever `next_start <= last_end` (this includes touching intervals); otherwise append a new interval.
4. Walk the merged intervals with a cursor initially at `0`. Each interval beginning after the cursor leaves a nonempty keep gap `[cursor, start)`. Advance the cursor to the interval’s end; after the walk, include `[cursor, duration_seconds)` if nonempty.
5. For each keep gap, set `duration = end - start`. Sum merged-interval lengths for `removed_duration_seconds` and keep durations for `output_duration_seconds`. Write only the four requested top-level keys using `json.dump`.

Half-open boundaries need no padding or one-second adjustment. Check that all keep intervals are ordered and nonempty, and that `original_duration_seconds == removed_duration_seconds + output_duration_seconds`.
