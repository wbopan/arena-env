# Prepare a compact fuzz seed manifest

Candidate seed files for a Python parser are in `/root/work/seeds`. They contain a mixture of JSON text, other UTF-8 text, and arbitrary bytes. Build a small, diverse seed selection without changing the seed files.

Classify each file independently: `json` if its bytes decode as UTF-8 and parse as a JSON value; otherwise `text` if the bytes decode as UTF-8; otherwise `binary`. For JSON seeds, define the deduplication key as the parsed value serialized with sorted object keys, separators `(',', ':')`, and `ensure_ascii=False`. For text and binary seeds, the deduplication key is the original byte sequence. Deduplicate only within a category. For each key, retain the file with the fewest original bytes, breaking ties by ascending filename.

From the retained files, select up to two per category, again ordered by byte length and then filename. Write `/root/work/seed_manifest.tsv` as UTF-8 tab-separated text. Its header must be `category\tfilename\tbytes\tsha256`. Rows must appear by category in the order `json`, `text`, `binary`, with the specified selection order within each category. `filename` is the basename, `bytes` is the original byte length, and `sha256` is the lowercase hexadecimal SHA-256 digest of the selected file's original bytes. Include no unselected files.
