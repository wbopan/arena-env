## Reference notes

Use Python’s standard-library `json` and `csv`; the browser-measurement scripts are unnecessary because the layout-shift entries are already captured.

```python
import json
import csv

with open('/root/work/shifts.json', encoding='utf-8') as f:
    pages = json.load(f)['pages']

with open('/root/work/cls_report.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['url', 'cls', 'rating', 'windows', 'max_window_start_ms'])
    # Write one row for each page, preserving pages order.
```

For each page, **filter out** entries whose `hadRecentInput` is true, then sort the remaining entries by numeric `startTime`. Track the current window’s first time, previous entry time, and score. Start a new window only when the gap from the previous counted entry is **greater than** 1000 ms or the elapsed time from the current window’s first entry is **greater than** 5000 ms; equality stays in the window. A window score is the sum of its `value` fields. CLS is the largest window score, not the sum across windows. Count all windows.

Keep the earliest window on a maximum-score tie (update the selected maximum only on a *strictly greater* score). For no counted entries, use CLS `0`, window count `0`, and an empty start-time field. Rate the **unrounded** CLS: `< 0.1` → `good`; `<= 0.25` → `needs-improvement`; otherwise → `poor`. Round only the CSV `cls` field to four decimal places, e.g. `f'{cls:.4f}'`. `csv.writer` handles URL quoting and the empty field.
