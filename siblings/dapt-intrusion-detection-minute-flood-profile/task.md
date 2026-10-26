# Occupied-minute flood profile

`/root/work/traffic.csv` contains a packet log with the header `ts,src_ip,dst_ip,src_port,dst_port,proto,length`. Timestamps are epoch seconds; rows are shuffled. Every row, including ARP, represents one captured packet. Compute the earliest timestamp, then assign each packet to minute index `floor((ts - earliest_timestamp) / 60)`. Only minutes containing packets participate in the rate statistics: do not insert empty minutes between occupied ones.

Write exactly `/root/work/minute_profile.json` as a JSON object with precisely these keys: `total_packets`, `occupied_minutes`, `average_ppm`, `peak_ppm`, `has_dos_pattern`, and `buckets`. `buckets` is an array sorted by increasing minute index. Each element has precisely `minute_index`, `packet_count`, and `share_percent`. The share is 100 times that bucket's count divided by `total_packets`, rounded to three decimal places as a JSON number. `average_ppm` is `total_packets / occupied_minutes`, rounded to three decimal places as a JSON number; `peak_ppm` is the largest occupied-minute count.

Determine `has_dos_pattern` using the unrounded average: it is a JSON boolean that is true only when `peak_ppm / average_ppm` is strictly greater than 20. The threshold concerns packet counts, not bytes, and a ratio equal to 20 is false. No other analysis flags or explanatory text belong in the output.
