# Half-open port-scan triage from a PCAP

`/root/work/capture.pcap` is a classic libpcap file (Ethernet link type, microsecond timestamps). It contains IPv4/TCP, IPv4/UDP and ARP frames.

Consider only IPv4 packets that carry TCP. Group them by IPv4 source address. For every source that sent at least 30 such packets, compute:

- `tcp_packets`: the number of TCP packets sent by the source.
- `unique_dst_ports`: the number of distinct TCP destination ports it sent to.
- `port_entropy`: the Shannon entropy (log base 2, in bits) of its TCP destination-port frequency distribution.
- `syn_only_ratio`: the fraction of its TCP packets whose flags have SYN (0x02) set and ACK (0x10) not set.
- `is_scanner`: true only if ALL three conditions hold: port_entropy > 5.0, syn_only_ratio > 0.7, and unique_dst_ports > 40.

Omit sources with fewer than 30 TCP packets entirely.

Write `/root/work/scan_report.json` with this shape:

```
{"sources": [{"src_ip": "10.1.0.7", "tcp_packets": 51, "unique_dst_ports": 51,
              "port_entropy": 5.6724, "syn_only_ratio": 1.0, "is_scanner": true}, ...],
 "scanners": ["10.1.0.7"]}
```

Formatting rules:

- Sort `sources` by IPv4 address in ascending numeric order (compare octet by octet).
- `scanners` lists the `src_ip` of every source with `is_scanner` true, in the same order.
- Write counts as JSON integers.
- Round `port_entropy` and `syn_only_ratio` to 4 decimals.
- Write `is_scanner` as a JSON boolean.
