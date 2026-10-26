## Reference notes

Use Python’s standard-library `csv`, `math`, and `json`; no clustering or optimization library is needed. Euclidean pixel distance is `math.hypot(cx - ex, cy - ey)`.

```python
import csv, json, math

with open(path, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
# CSV values are strings: convert IDs with int(...) and coordinates with float(...).

with open(output_path, "w", encoding="utf-8") as f:
    json.dump({"images": image_results}, f, ensure_ascii=False)
```

Process the **union** of `file_rad` values from both CSVs, in sorted order. Within each image, form candidate centroid–expert pairs only; images with an empty side still need an output object. For each pair, compute distance, retain it if `distance <= 16`, and sort candidates by `(unrounded_distance, cluster_id, expert_id)`. Traverse once, accepting a pair only when both IDs are unused in that image. This is greedy matching, **not** a global assignment.

Keep full-precision distances through filtering, sorting, and acceptance; apply `round(distance, 3)` only when constructing accepted match objects. Sort unmatched IDs numerically, and emit empty lists rather than omitting fields. Each image object and match object should contain only the fields specified in the task.
