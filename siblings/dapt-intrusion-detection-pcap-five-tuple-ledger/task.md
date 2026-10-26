# Five-tuple flow ledger

Analyze `/root/work/capture.pcap`. It is a classic little-endian libpcap capture with Ethernet frames and microsecond timestamps. It contains IPv4 TCP and UDP packets as well as ARP frames. A flow is the unique five-tuple `(source IPv4, destination IPv4, source port, destination port, protocol)`. Exclude frames that are not IPv4 TCP or IPv4 UDP; do not use timestamps to split flows. Repeated packets with the same five-tuple belong to one flow.

Write exactly `/root/work/flows.tsv`, a UTF-8 tab-separated file. Use this exact header: `proto	src_ip	dst_ip	src_port	dst_port	packet_count	total_bytes	has_reverse`. Include one row per observed flow, sorted lexicographically by `(proto, src_ip, dst_ip, src_port, dst_port)`, with ports compared as integers. Protocol values are uppercase `TCP` and `UDP`; ports and counts are decimal integers without formatting. `total_bytes` sums the captured Ethernet-frame lengths from the PCAP record headers, in bytes, including Ethernet headers.

Set `has_reverse` to lowercase `true` if the capture also contains the five-tuple with source and destination IPs exchanged and source and destination ports exchanged, with the same protocol. Otherwise write `false`. This is a property of each directed flow: if two distinct reverse flows exist, both rows say `true`. Do not add a totals row or interpret TCP flags as separate flows.
