## Reference notes

- Use Python standard library: `csv.reader(..., delimiter="\t")` for the headerless TSV files, `bisect.bisect_right` for successor lookup, and `json.dump` for the output. Convert every field with `int`; the inputs contain unsigned decimal integers.
- Column positions:
  - `writes.tsv`: `txn_seq, key_hash, new_wts, ats_at_write`
  - `aborts.tsv`: `txn_seq, key_hash, local_wts, current_wts, commit_ts, ats_at_abort`
- Build a **per-key** sorted list of `new_wts` values from committed writes. File row order does not establish timestamp order. For an abort row, its successor is the smallest timestamp for that key **strictly greater** than `local_wts`:

  ```python
  from bisect import bisect_right

  timestamps = sorted(writes_by_key[key_hash])
  pos = bisect_right(timestamps, local_wts)
  successor = timestamps[pos]  # if a successor exists
  ```

- The read version’s validity interval ends immediately before `successor`: `[local_wts, successor)`. Thus the row is unnecessary exactly when `commit_ts < successor`; equality is **necessary**. Do not substitute `current_wts`, access timestamps, transaction ids, or another key’s writes for the successor.
- Aggregate **all** abort rows by `txn_seq`: include a transaction only when every one of its rows is unnecessary. Deduplicate and sort the integer ids before writing a JSON array to `/root/work/unnecessary_aborts.json`.
- Cheap workflow: inspect file sizes and a few lines to confirm shape; write one Python script to build per-key timelines, classify rows, aggregate by transaction, and emit JSON; run it, then inspect the output’s JSON shape and a small summary of row/transaction counts.
