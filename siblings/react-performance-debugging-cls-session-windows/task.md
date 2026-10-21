# Cumulative Layout Shift report

The file `/root/work/layout_shifts.jsonl` holds layout-shift performance entries captured in a browser for several pages of a web app. Each line is a JSON object with these fields:

- `page`
- `startTime` (ms since navigation)
- `value` (layout shift score)
- `hadRecentInput` (bool)

Lines from different pages are interleaved and not sorted.

Compute the CLS of each page using the Core Web Vitals session-window definition:

1. Ignore entries with `hadRecentInput: true`.
2. Process the remaining entries of a page in ascending `startTime`. A shift joins the current session window only if both conditions hold:
   - it occurs less than 1000 ms after the previous shift, and
   - it occurs less than 5000 ms after the first shift of the window.

   Otherwise it starts a new window.
3. A window's score is the sum of its `value`s. The page CLS is the largest window score. If windows tie, the earliest one wins.

Rating: `good` if CLS <= 0.1, `needs-improvement` if CLS <= 0.25, otherwise `poor`.

Write `/root/work/cls_report.csv` with this header:

`page,cls,rating,shift_count,worst_window_start_ms`

Write one row per page, sorted by `page` in ascending plain string order. The columns are:

- `cls`: 4 decimals.
- `shift_count`: the number of shifts counted (entries with `hadRecentInput: true` excluded).
- `worst_window_start_ms`: the `startTime` of the first shift in the highest-scoring window, with 1 decimal.

Every page has at least one counted shift.
