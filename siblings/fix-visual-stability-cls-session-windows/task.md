# CLS session-window report

A browser trace of layout-shift entries was captured for several pages of a web shop. It is stored in `/root/work/shifts.json` with the shape `{"pages": [{"url": str, "entries": [{"startTime": ms, "value": float, "hadRecentInput": bool}, ...]}, ...]}`. Entries within a page are **not** in chronological order.

Compute the Cumulative Layout Shift (CLS) of every page using the standard session-window definition:

- Ignore entries with `hadRecentInput == true`.
- Process the remaining entries in ascending `startTime`.
- An entry starts a new session window if it is the first entry, or if its `startTime` is more than 1000 ms after the previous entry's `startTime`, or more than 5000 ms after the `startTime` of the first entry of the current window.
- A window's score is the sum of its entries' `value`. CLS is the maximum window score (0 if there are no counted entries).

Rating, applied to the unrounded CLS: `good` if CLS < 0.1, `needs-improvement` if 0.1 <= CLS <= 0.25, `poor` if CLS > 0.25.

Write `/root/work/cls_report.csv` with header exactly:

`url,cls,rating,windows,max_window_start_ms`

One row per page, in input order. `cls` rounded to 4 decimals; `windows` is the number of session windows; `max_window_start_ms` is the `startTime` (as given in the input) of the first entry of the highest-scoring window (the earliest such window on ties), or empty if the page has no counted entries.
