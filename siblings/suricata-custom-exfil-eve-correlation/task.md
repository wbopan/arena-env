Reconcile Suricata HTTP and alert events from an offline investigation. Alerts alone do not identify which HTTP transaction met the investigation criteria.

Input: `/root/work/eve.json`, newline-delimited JSON. Relevant records have `event_type` equal to `http` or `alert`. Both event types carry integer `flow_id` and `tx_id`. An HTTP record also has `src_ip` and an `http` object containing `http_method`, `url`, `x_tlm_mode`, and `request_body_len`. An alert record has `alert.signature_id`. Events may appear in any order.

A transaction counts when its HTTP record has method `POST`, URL exactly `/telemetry/v2/report`, and `x_tlm_mode` exactly `exfil`, and at least one alert for the same `(flow_id, tx_id)` has signature ID `1000001`. Other signatures do not count. Multiple qualifying alerts on one transaction count only once. Attribute the transaction to the HTTP record's `src_ip`, not the alert record's address. All lengths are bytes.

Write `/root/work/source_totals.csv` with the exact header `src_ip,transactions,body_bytes`. Include one row per source with at least one counted transaction, sorted by the numeric value of the IPv4 address. `transactions` is the number of distinct counted transactions; `body_bytes` is the sum of their `request_body_len` values. Use integer decimal fields and no totals row.
