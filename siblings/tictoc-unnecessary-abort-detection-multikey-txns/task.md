A TicToc validator aborts a transaction when the version it read of a key (identified by `local_wts`) is no longer the current version at validation time. Some of these aborts are unnecessary, because the version that was read was still the valid version at the transaction's candidate commit timestamp.

Inputs are in `/root/work`. Both files are tab-separated, have no header, and contain only unsigned decimal integers.

`writes.tsv` holds committed writes, in arbitrary row order. Its columns are `txn_seq`, `key_hash`, `new_wts`, `ats_at_write`.

`aborts.tsv` holds failed read validations. Its columns are `txn_seq`, `key_hash`, `local_wts`, `current_wts`, `commit_ts`, `ats_at_abort`.

A single aborted transaction may have several rows in `aborts.tsv`, one for each read key that failed validation.

**Validity rule.** The version of a key with write timestamp `local_wts` is valid from `local_wts` up to `s - 1`. Here `s` is its successor: the smallest `new_wts` in `writes.tsv` for the same key that is strictly greater than `local_wts`.

**Unnecessary row.** A row is unnecessary if `commit_ts < s`. If `commit_ts >= s`, the row is a necessary abort.

**Unnecessary transaction.** A transaction is unnecessarily aborted only if every one of its rows in `aborts.tsv` is unnecessary.

Write `/root/work/unnecessary_aborts.json` containing a JSON array of the `txn_seq` values of all unnecessarily aborted transactions. The ids must be integers, sorted ascending, and each id may appear only once.
