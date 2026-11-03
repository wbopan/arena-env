# Normalise a media catalogue and build a playlist

`/root/work/library.csv` has columns `asset_id, title, duration, updated_at`. Durations come in mixed forms: `H:MM:SS`, `M:SS`, `<n>s` and `<h>h<m>m<s>s` with any part omitted (for example `1h5s`, `42m`). Asset ids are case-insensitive, and some assets appear more than once: keep only the row with the latest `updated_at` (ISO timestamps). `/root/work/job.json` gives `playlist_cap_sec`.

Write `/root/work/catalog.json` with:
- `items`: one item per asset, sorted by upper-case id: `{"asset_id": upper-case id, "title": trimmed with inner space runs collapsed to one, "duration": ISO 8601 duration, "duration_sec": integer seconds}`. The ISO form is `PT` then hours `H`, minutes `M`, seconds `S`, leaving out zero parts (`PT1H5S`, `PT42M`); zero is `PT0S`.
- `playlist`: asset ids chosen greedily: go through the items from shortest to longest (ties by id) and add each one whose duration still fits so the total stays at or under `playlist_cap_sec`; skip ones that do not fit and keep going.
- `playlist_sec`: the playlist's total seconds.
