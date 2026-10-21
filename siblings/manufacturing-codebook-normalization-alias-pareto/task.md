Engineers type defect reasons with typos, abbreviations and inconsistent separators. Map each reason to a standard code and build a per-product Pareto.

Inputs:
- /root/work/logs.csv has the columns record_id, product_id, station and reason_text (one reason per record).
- /root/work/alias_table.csv has the columns product_id, alias and code.
- /root/work/codebook.csv has the columns product_id, code, standard_label and station_scope. station_scope is '|'-separated; empty means all stations.

Text normalization (apply to both reasons and aliases):
1. Lowercase.
2. Replace `-`, `_` and `.` with a space.
3. Collapse whitespace runs to a single space.
4. Strip.

Mapping a record:
- Compare its normalized reason with every normalized alias of the same product, using character-level Levenshtein distance (insert, delete and substitute each cost 1).
- Take the alias with the minimum distance. If several aliases tie, use the one whose code is lexicographically smallest.
- If the minimum distance is greater than 2, the record is `UNKNOWN`.
- If the chosen code has a non-empty station_scope that does not contain the record's station, the record is also `UNKNOWN`.

Output /root/work/pareto.json:
{"total_records": int, "unknown_records": int, "products": {"<product_id>": [{"code": str, "label": str, "count": int, "share": float}, ...]}}

Output rules:
- Include every product_id that appears in logs.csv.
- Each list contains only codes with count > 0, including `UNKNOWN` (whose label is "").
- Sort each list by count descending, then by code ascending (plain string comparison).
- label is the codebook standard_label.
- share = count / number of records of that product, rounded to 4 decimals.
