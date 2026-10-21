1. `cat /root/network_stats.csv` to get the metric names, and grep `def`/`return` in `/root/skills/pcap-analysis/pcap_utils.py` to see the helper signatures.
2. Write one script that loads the pcap with `load_packets` and `split_by_protocol`, and uses the helpers (`graph_metrics`, `flow_metrics`, `iat_stats`, `packets_per_minute_stats`, `producer_consumer_counts`, entropy, `detect_*`). Compute anything not covered manually: population variance, `int((ts-start)/60)` buckets, unique-IP degrees.
3. Rewrite `/root/network_stats.csv` in place: keep `#` lines and the header, fill only the values, and write flags as lowercase true/false.
4. Re-read the non-comment lines and confirm no value is empty and the sanity checks hold.
