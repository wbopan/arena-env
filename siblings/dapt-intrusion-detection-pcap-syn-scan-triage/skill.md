## Reference notes

Use Python’s standard library (`struct`, `collections`, `math`, `ipaddress`, `json`). The skill’s `detect_port_scan()` is **not suitable here**: it uses different minimum-volume and scan thresholds. Compute the task’s per-source fields directly.

- Classic libpcap starts with a 24-byte global header. Magic bytes `d4 c3 b2 a1` mean little-endian; `a1 b2 c3 d4` mean big-endian. Each packet has a 16-byte record header: `ts_sec, ts_usec, incl_len, orig_len`, unpacked with `endian + 'IIII'`. Read exactly `incl_len` bytes for that frame; timestamps are unnecessary.
- For an ordinary Ethernet frame, the EtherType is at bytes `12:14`; IPv4 is `0x0800`, and its header starts at byte 14. Check lengths before accessing offsets. IPv4 version must be 4; header length is `(frame[ip_start] & 0x0f) * 4` bytes; protocol byte is at `ip_start + 9` and TCP is `6`. IPv4 source bytes are `ip_start + 12 : ip_start + 16`.
- TCP starts after the IPv4 header. A noninitial IPv4 fragment has no TCP header to parse (`fragment_field & 0x1fff != 0`). Where a TCP header is present, destination port is its bytes `2:4` (network/big-endian order), and flags are byte `13`. SYN-only means `(flags & 0x02) != 0 and (flags & 0x10) == 0`; other flags do not disqualify it.

For each source, maintain a TCP packet count, `Counter` of destination ports, and SYN-only count. Omit sources with count `< 30`. For port counts \(c_i\) and total \(N\):

```python
entropy = -sum((c / N) * math.log2(c / N) for c in port_counts.values())
ratio = syn_only_count / N
unique_ports = len(port_counts)
```

Apply **strict** comparisons to unrounded values: `entropy > 5.0 and ratio > 0.7 and unique_ports > 40`. Round the two reported floats to four decimals *after* classification. Sort source addresses numerically with `ipaddress.IPv4Address`; derive `scanners` from the sorted source entries. `json.dump()` writes Python `int` as JSON integers and `bool` as JSON booleans.
