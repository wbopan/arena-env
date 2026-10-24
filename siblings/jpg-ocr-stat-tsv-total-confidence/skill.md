## Reference notes

- OCR is already complete. Read the TSVs directly; do **not** re-run Tesseract or inspect the JPGs. The OCR skill’s `image_to_data` output is word-level data, but its example confidence calculation does **not** implement this task’s `level == 5` and `conf >= 30` filters.
- Use standard-library `csv.DictReader(f, delimiter="\t")` to preserve the named TSV columns. TSV fields are strings: convert `level`, `block_num`, `par_num`, `line_num`, and `word_num` to `int`, and `conf` to `float`. Keep `text` only when `text.strip()` is nonempty.
- Group kept rows by the **numeric** `(block_num, par_num, line_num)` tuple. Sort each group by numeric `word_num`, join texts with one space, then sort the group keys numerically. Do not use file-row order, image coordinates, or lexicographic ordering of numeric fields.

```python
from collections import defaultdict
import csv
from pathlib import Path

groups = defaultdict(list)
confidences = []
with Path(tsv_path).open(newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        text = row["text"].strip()
        conf = float(row["conf"])
        if int(row["level"]) != 5 or conf < 30 or not text:
            continue
        key = tuple(int(row[k]) for k in ("block_num", "par_num", "line_num"))
        groups[key].append((int(row["word_num"]), text))
        confidences.append(conf)

lines = [
    " ".join(text for _, text in sorted(groups[key]))
    for key in sorted(groups)
]
```

- For total selection, check keyword **groups** in priority order; within a group, scan eligible lines in reading order. Both keyword and exclusion checks are case-insensitive **substring** checks. Exclude a candidate line containing any of `SUBTOTAL`, `SUB TOTAL`, `TAX`, `GST`, `SST`, `DISCOUNT`, `CHANGE`, `CASH`.
- Once the first eligible matching line in the highest matching group is selected, do **not** try another keyword or matching line if its amount is absent. Search that line, then only the immediately following rebuilt line. Use `re.findall(r"\d{1,3}(?:,\d{3})+\.\d{2}|\d+\.\d{2}", line)` and take the **last** match from the first line that has matches. If neither has one, use JSON `null`. Remove commas from a found amount; retain two decimal places as a **string**.
- `word_count = len(confidences)`; `mean_conf` is the mean of those same kept words, rounded to two decimals. Serialize via `json.dump`: Python `None` becomes JSON `null`, while the confidence must be a JSON number. Iterate `sorted(Path("/root/work/ocr").glob("r*.tsv"))`, derive each JPG filename with `path.with_suffix(".jpg").name`, and write one object per file with only the four requested keys. After writing, read the JSON back and inspect its record count, ordering, keys, and value types.
