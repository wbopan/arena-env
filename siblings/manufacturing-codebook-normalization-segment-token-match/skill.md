## Reference notes

Use Python’s standard-library `csv` and `re`; the task specifies an exact token-overlap rule, so do not use fuzzy or semantic matching from the skill document.

```python
import csv
import re

def tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))

def segments(text):
    return [part.strip() for part in re.split(r"[/;+,]", text)
            if part.strip()]
```

- Read both files with `csv.DictReader(open(path, newline="", encoding="utf-8"))`. Keep log rows in file order and treat IDs and codes as strings.
- For each codebook row, form `K` from `tokens(standard_label)` **unioned** with tokens from every `keywords.split("|")` entry. An empty keyword contributes no tokens.
- Candidate filtering is by matching `product_id`, then station: an empty `station_scope` allows every station; otherwise require the record’s station to be a member of `station_scope.split("|")`.
- For each segment, compute `len(T & K) / len(T)` (or `0` when `T` is empty). Select the highest-scoring candidate; for equal scores, select the lexicographically smallest `code`. Apply the `0.5` threshold **after** selecting the best candidate. With no candidate, the score is `0`.
- Number only retained, nonempty segments, starting at `S1`. Preserve each stripped piece as `span_text`; do not lowercase it in the output.
- Write with `csv.writer(open(path, "w", newline="", encoding="utf-8"))`, using exactly the requested header and column order. Formatting a score as `f"{score:.4f}"` gives four decimal places, including for `UNKNOWN` rows. CSV writing handles quoting of commas and other special characters.
