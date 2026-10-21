# Opening Removal and Compression Report

A lecture recording has already been analysed.

Inputs:
- `/root/work/energies.json`: the per-second RMS energy profile.
  - Key `energies` is a list; element i is the energy of second [i, i+1).
  - `window_seconds` is 1.
- `/root/work/pauses.json`: pause segments from a pause detector.
  - Key `segments` is a list of `{"start", "end", "duration"}` objects, in seconds, with `end` exclusive.
  - The segments are unsorted. They may overlap, touch each other, or extend past the end of the recording.

Steps:
1. **Detect the opening.** Let baseline = median of the first 20 energies. The opening ends at the first second i such that energies i, i+1 and i+2 are all strictly greater than 3 x baseline. The opening segment is [0, i). If no such i exists, the opening end is 0 and there is no opening segment.
2. **Combine and merge.**
   - Combine the opening segment (if non-empty) with all pause segments.
   - Let D = number of energy values. Clip each segment to [0, D] and drop empty ones.
   - Sort by start and merge segments that overlap or touch (next start <= current end).
3. **Write the report** to `/root/work/compression_report.json`:

```json
{
  "original_duration_seconds": <D>,
  "opening_end_seconds": <i>,
  "compressed_duration_seconds": <number>,
  "removed_duration_seconds": <number>,
  "compression_percentage": <number>,
  "segments_removed": [{"start": <number>, "end": <number>, "duration": <number>}]
}
```

Report fields:
- `removed_duration_seconds` is the sum of the merged segment durations.
- `compressed_duration_seconds` = D - removed.
- `compression_percentage` = removed / D x 100, rounded to 2 decimals.
- `segments_removed` is the merged list sorted by start, with `duration = end - start`.
- All times are in seconds.
