## Reference notes

Use Python’s standard-library `struct`, `socket`, `re`, and `json` for a packet-by-packet pass. `tshark -r /root/work/traffic.pcap -x` can help inspect raw bytes, but HTTP dissection filters may miss traffic on unusual ports; parse TCP payloads directly for the final pass.

**Classic libpcap framing**
- The global header is 24 bytes. Its first four bytes determine byte order: `d4 c3 b2 a1` or `4d 3c b2 a1` → little-endian; `a1 b2 c3 d4` or `a1 b2 3c 4d` → big-endian. The latter two are nanosecond-timestamp variants; timestamp precision does not affect this task.
- Each record has a 16-byte header, unpacked as `IIII` in the selected byte order. The third field, `incl_len`, is the number of packet bytes to read. Increment the 1-based packet index for **every** record, including ACKs and responses.
- For Ethernet, read the EtherType at bytes `12:14` (`0x0800` for IPv4). IPv4 begins at offset 14. Its header length is `(first_byte & 0x0f) * 4`; protocol byte `9` must be `6` for TCP. Use the IPv4 *total length* (bytes `2:4`) to bound the IP packet rather than including Ethernet padding.
- TCP starts after the IPv4 header. Source port is its first two bytes (network byte order); TCP header length is `(tcp_byte_12 >> 4) * 4`. Payload begins after that header. Check lengths before slicing; skip malformed/truncated records. `socket.inet_ntoa(ip_header[12:16])` formats the source address.

**HTTP matching on payload bytes**
- Ignore empty payloads and responses. Parse the first request line into method, request-target, and HTTP version; compare method and target **exactly** as bytes. Do not infer HTTP from the TCP port.
- Split headers from body at the **first** HTTP blank line (normally `b"\r\n\r\n"`). Compare header names case-insensitively, and trim surrounding whitespace from a header value before its exact comparison. Keep header parsing separate from body parsing.
- Split the body on `b"&"` and each pair on its **first** `b"="` only. Do not URL-decode. Treat the conditions as existence checks for qualifying `blob` and `sig` parameters.
- Use `re.fullmatch` on each parameter value, not `re.search`: Base64-looking is `rb"[A-Za-z0-9+/]+={0,2}"` with **total value length at least 80**, including padding; signature is `rb"[0-9A-Fa-f]{64}"`. Full matching prevents extra characters or misplaced `=` from passing.

A compact pass structure is: read global header → iterate record headers and `incl_len` bytes → extract bounded Ethernet/IPv4/TCP payload → parse and check the request → append `{"packet": index, "src": f"{address}:{port}"}`. Iteration already preserves packet order; write `{"count": len(alerts), "alerts": alerts}` with `json.dump`.
