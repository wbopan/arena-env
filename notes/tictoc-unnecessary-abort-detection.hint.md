1. Inspect both TSVs with `wc`/`head` and a Python Counter. Check rows per txn and whether same-txn rows share `commit_ts`/`ats`.
2. In plain Python with `csv`, group writes per key and label each abort row unnecessary iff no write on that key has `local_wts < new_wts <= commit_ts` and `ats_at_write < ats_at_abort`.
3. A txn counts if all failing rows of an abort event pass. Dedupe and sort the ids, then write the JSON int array to `/root/unnecessary_aborts.json`.
4. Verify the file is sorted, unique, and all ints, and compare the counts across the boundary variants.
