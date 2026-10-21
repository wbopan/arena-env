# Per-pair C2 beaconing report

`/root/work/traffic.csv` is a packet log.

- Its header is `ts,src_ip,dst_ip,src_port,dst_port,proto,length`.
- `ts` is epoch seconds with millisecond precision; `length` is the packet size in bytes.
- Rows are NOT in time order.
- Some rows (e.g. ARP) have empty IP fields. Ignore any row whose `src_ip` or `dst_ip` is empty.

Group packets by directed IP pair (src_ip, dst_ip). Ports and protocol are ignored, and A->B is a different pair from B->A. Keep only pairs with at least 10 packets.

For each kept pair compute:

- `packets`: the number of packets.
- `total_bytes`: the sum of `length`.
- Inter-arrival times (IATs): sort the pair's timestamps ascending; the IATs are the differences between consecutive timestamps.
- `iat_mean`: the mean IAT in seconds, rounded to 3 decimals.
- `iat_cv`: the coefficient of variation, i.e. the population standard deviation of the IATs (divide by N) divided by the mean IAT, rounded to 4 decimals. Use 0 if the mean is 0.
- `is_beacon`: `true` if the unrounded iat_cv is below 0.5 (regular, robotic timing typical of C2 beaconing), otherwise `false`.

Write `/root/work/beacon_report.csv`:

- The header must be exactly `src_ip,dst_ip,packets,total_bytes,iat_mean,iat_cv,is_beacon`.
- Write one row per kept pair.
- Sort rows by src_ip, then dst_ip, using plain string (lexicographic) comparison.
- Write booleans as lowercase `true` / `false`.
