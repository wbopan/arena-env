You are triaging a packet capture for a custom data-exfiltration pattern hidden in HTTP telemetry traffic. The IDS sensor was down, so you must apply the detection logic yourself, offline.

Input: `/root/work/traffic.pcap`. It is a classic libpcap file with Ethernet link type, IPv4 and TCP. Each HTTP message is carried entirely in the payload of one TCP packet. The capture also contains empty ACK packets and HTTP responses. HTTP may use any TCP port.

A packet is an exfil hit only when its TCP payload is an HTTP request and all of these are true:
1. The method is exactly `POST`.
2. The request-target is exactly `/telemetry/v2/report`. The match is case-sensitive, and no query string or trailing slash is allowed.
3. A header named `X-TLM-Mode` has the value `exfil`.
   - The header name is case-insensitive.
   - The value must equal `exfil` exactly after trimming surrounding whitespace.
4. The body has a `blob` parameter with a Base64-looking value of at least 80 characters.
   - The body starts after the first blank line and is `&`-separated `key=value` pairs. Split each pair at the first `=`.
   - Do not URL-decode anything.
   - Base64-looking means one or more characters from `A-Z a-z 0-9 + /`, followed by at most two `=` padding characters at the end only.
   - The length count includes padding.
5. The body has a `sig` parameter whose value is exactly 64 hex characters, in either case.

Write `/root/work/alerts.json` in this form:

`{"count": N, "alerts": [{"packet": 12, "src": "10.1.2.3:40001"}, ...]}`

- `packet` is the 1-based index of the record in the pcap file.
- `src` is the client IPv4 address and TCP source port.
- Sort `alerts` by `packet` in ascending order.
- `count` is the number of alerts.
