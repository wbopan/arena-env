**Inputs (inspect cheaply first)**
- Find the files: `ls -la /app/data/`. There is `test_center_logs.csv` plus one codebook per product, which may be CSV or JSON.
- Check the CSV columns, row count and encoding:
  - `python3 -c "import pandas as pd;d=pd.read_csv('/app/data/test_center_logs.csv');print(d.shape);print(d.columns.tolist());print(d.head(3).to_string())"`
  - Expect at least: record_id, product_id, station, engineer_id, raw_reason_text. It may also have fail_code and test_item.
  - Text is mixed Chinese and English. Read files with `encoding='utf-8'` and write JSON with `ensure_ascii=False`.
- Peek at one codebook's structure before coding, for example `head -c 800 file`, or print `keys`/columns and one entry.
- Typical entry fields are: code, standard_label, keywords_examples (a list or a delimited string), category/categories, and stations.
- Check `stations`:
  - It may be null/None/NaN/empty, meaning valid at all stations.
  - Otherwise it is a list or delimited string of allowed stations.
- Map each product_id to its codebook. Check how product IDs appear in the codebook filenames or inside the files.
- Check values: `d.product_id.value_counts()`, `d.station.unique()`.

**Domain rules from the skill**
- **Valid codes.** `pred_code` must be a code from *that record's product* codebook, or "UNKNOWN". `pred_label` must be that entry's exact standard_label, or "" when UNKNOWN. Do not use another product's codebook: the same term can mean different codes across products.
- **Station scope.** If `entry.stations` is not None/empty, the code is valid only when the record's station matches one of the listed stations. Normalize case and whitespace before comparing. Filter out non-matching candidates before ranking.
- **Segmentation.** Split raw_reason_text into 1..N segments.
  - Split on delimiters such as `/ + ; ； , ， 、 | & 及 和 并` and newlines. Also split on " and ", " then ", "after" if useful.
  - Keep each span as an exact substring of raw_reason_text: strip whitespace but do not alter characters. Drop empty pieces.
  - If nothing survives, use the whole text as one segment.
  - Verify with `assert span in raw`.
- **Segment ids.** Use `segment_id = f"{record_id}-S{i}"` with i starting at 1, in order.
- **Scoring each candidate.** Combine several kinds of evidence into a score in [0,1]:
  - Text similarity between the span and the label, each keyword/example, and the category. Use the max of fuzzy ratio, `partial_ratio` and token-overlap Jaccard, computed on lowercased text.
  - Chinese substring hits: check whether any keyword is contained in the span, or the span in the keyword.
  - Abbreviation hits, e.g. OS→open/short, NG, 虚焊 = cold solder, 接触不良 = poor contact, 治具 = fixture.
  - A station-compatibility bonus.
  - fail_code and test_item alignment: these columns' tokens overlapping the entry text.
  - A penalty for conflicting cues.
  - Example weights: `s = 0.55*text + 0.15*kw_hit + 0.1*station_ok + 0.1*failcode_align + 0.1*testitem_align`, clipped to [0,1].
- **Ranking and tie-break.** Sort candidates descending to get s1 (top) and s2 (second).
  - Near-best set: all candidates with score ≥ s1 − 0.02.
  - If there are several, pick one deterministically, e.g. `idx = int(hashlib.md5(f"{record_id}|{i}|{station}|{fail_code}|{test_item}".encode()).hexdigest(),16) % len(near)` over the near set sorted by code. Do not use Python's `hash()`, which is randomized per run.
- **UNKNOWN.** Decide it from the best candidate only.
  - If s1 < threshold (e.g. ~0.35–0.45; tune by looking at the score distribution), output `pred_code="UNKNOWN"` and `pred_label=""`.
  - Strong component or keyword hits should rarely end up UNKNOWN. Generic or noise segments ("NG", "retest", "ok") more often should.
  - Aim for a modest UNKNOWN share: neither 0% nor a majority.
- **Confidence.** This is an engineering calibration, not a probability. Round to 4 decimals.
  - Known: `conf = 0.55 + 0.4*s1 + 0.15*(s1-s2)`, clipped to about [0.5, 0.99].
  - UNKNOWN: `conf = 0.1 + 0.5*s1`, clipped to about [0.05, 0.45].
  - This guarantees separation: the UNKNOWN mean, quantiles and max should be below the known ones.
  - Values must vary, not be near-constant. Check the std and the number of unique values.
  - Confidence should rise weakly with evidence strength.
- **Rationale.** A short string that includes the station, fail_code, test_item, the matched token or keyword overlap, or a component reference. Example: `"station=ICT; fail_code=OS; test_item=VDD_3V3; matched kw '虚焊' -> label; score=0.71, margin=0.12"`. For UNKNOWN, say the best score was weak and name the best candidate.

**Libraries**
- pandas, json, re and hashlib.
- For fuzzy matching, use `rapidfuzz` (`fuzz.ratio`, `fuzz.partial_ratio`, `fuzz.token_set_ratio`, divide by 100) if it is installed. Test with `python3 -c "import rapidfuzz"`, and try `pip install rapidfuzz` if it is missing.
- If it is unavailable, use `difflib.SequenceMatcher(None,a,b).ratio()`.
- Tokenizer: English words via `re.findall(r'[a-z0-9]+')` plus individual CJK characters or bigrams via `re.findall(r'[\u4e00-\u9fff]')`, so Chinese overlap counts.

**Step-by-step plan**
1. Run `ls /app/data`, inspect the CSV columns, head and size, and look at one codebook entry's structure (field names and stations format).
2. Write `/app/solve.py`:
   - Load the logs and codebooks.
   - Build `valid_code_set[product]`, `station_scope_map[product][code]` and a list of entries per product.
   - Segment, score, filter by station, rank, tie-break, apply UNKNOWN, compute confidence, write the rationale.
3. `mkdir -p /app/output`, then write `/app/output/solution.json` with `json.dump(out, f, ensure_ascii=False, indent=2)`.
4. Run the script. Print summary statistics only: number of records versus CSV rows, number of segments, UNKNOWN rate, and confidence mean, quantiles and unique-count for known versus UNKNOWN. Also print the top predicted codes.
5. Validate with a short checker:
   - Every CSV record appears exactly once.
   - segment_ids follow the pattern and are sequential.
   - span_text is a substring of raw_reason_text.
   - pred_code is in that product's codebook or is UNKNOWN.
   - pred_label equals the codebook label, and is "" for UNKNOWN.
   - Station scope is respected.
   - 0 ≤ confidence ≤ 1, rounded to 4 decimals.
   - max(UNKNOWN confidence) < mean(known confidence).
6. Spot-check about 5 records, printing only the raw text, spans and codes. Tune the threshold and keyword/abbreviation map if matches look wrong, then rerun.

**Output format (exact)**
- `/app/output/solution.json` is shaped as `{"records":[{record_id, product_id, station, engineer_id, raw_reason_text, normalized:[{segment_id, span_text, pred_code, pred_label, confidence, rationale}]}]}`.
- Record fields are copied as strings from the CSV.
- confidence is a JSON number, not a string.
- Every record has at least one segment.
