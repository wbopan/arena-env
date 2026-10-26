## Reference notes

Use Python’s standard-library `struct`, `socket`, `collections`, and `csv`; no packet-analysis library is needed. The capture is **classic little-endian PCAP**, not PCAPNG.

```python
import struct
import socket
from collections import defaultdict

with open('/root/work/capture.pcap', 'rb') as f:
    global_header = f.read(24)
    # Little-endian PCAP magic: b'\xd4\xc3\xb2\xa1'
    # Link type is the uint32 at offset 20; Ethernet is 1.
    while header := f.read(16):
        ts_sec, ts_usec, incl_len, orig_len = struct.unpack('<IIII', header)
        frame = f.read(incl_len)
        # Process frame here.
```

`incl_len` is the **captured Ethernet-frame length** and is the value to add to `total_bytes`; do not substitute `orig_len`, the IPv4 total length, or a reconstructed packet length. Timestamps do not affect flow identity.

For an Ethernet frame, bytes `12:14` are the big-endian EtherType (`0x0800` for IPv4); the IPv4 header starts at offset 14. Check lengths before reading fields. In the IPv4 header, the low four bits of its first byte give the header length in 32-bit words; protocol is byte 9 (`6` TCP, `17` UDP); source and destination addresses are bytes `12:16` and `16:20` (convert with `socket.inet_ntoa`). The TCP/UDP header starts after the variable-length IPv4 header; its first four bytes are source and destination ports, unpacked with `struct.unpack('!HH', ...)`. A non-initial IPv4 fragment has no transport header at that position, so do not infer ports from its payload.

Accumulate by the **directed** key `(proto, src_ip, dst_ip, src_port, dst_port)`, incrementing count and adding `incl_len` for each eligible record. After collecting keys, the reverse lookup key is `(proto, dst_ip, src_ip, dst_port, src_port)`. Sort keys directly in that order: strings compare lexicographically and ports remain integers.

For output, `csv.writer(file, delimiter='\t', lineterminator='\n')` writes TSV. Open with `encoding='utf-8', newline=''`; write the task’s exact header, then one row per key with lowercase `true`/`false`.
