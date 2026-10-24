## Reference notes

Use Python standard-library `json`, `csv`, `re`, and `collections.defaultdict`; this is a direct lookup across two known files. The task’s reviewer rule is **exactly** the six-word threshold, not a judgment about whether feedback is substantive.

```python
with open("/root/work/DATA/slack.json", encoding="utf-8") as f:
    messages = json.load(f)  # list of message dictionaries

with open("/root/work/DATA/employees.csv", newline="", encoding="utf-8") as f:
    employees = list(csv.DictReader(f))
```

- Build the employee lookup by **`(team, name)`**, not name alone: display names can repeat across teams.
- Keep only messages whose channel starts with `planning-` and has a nonempty product suffix. Resolve each author using that message’s channel product and `user_name`.
- A share must have `parent_id is None` and a doc link in `text`. Extract the ID with `re.search(r"/archives/docs/(doc_[0-9a-f]+)(?![0-9A-Za-z_])", text)`. Replies are never shares.
- Index eligible replies by `parent_id` so each share’s replies can be found without rescanning the whole list. `n_replies` counts **all** such replies, including short replies and replies by the sharer.
- For reviewer IDs, use only reply authors with `len(reply["text"].split()) >= 6`; exclude the sharer, deduplicate with a set, then `";".join(sorted(ids))`. `str.split()` implements whitespace-separated words.
- Sort output rows by `doc_id`. Write with `csv.DictWriter`, `newline=""`, and field order `["product", "doc_id", "sharer_id", "n_replies", "reviewer_ids"]`; call `writeheader()`. An empty reviewer set becomes an empty string, not `[]` or a null value.

After writing, inspect the CSV header and a few rows, and check that the number of output rows equals the number of qualifying top-level shares.
