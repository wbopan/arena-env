1. Use tshark `-T fields` (method, uri, http.file_data, cut to 300 chars) on train_pos and train_neg to see the body encoding and how the negatives differ.
2. Write one single-line rule into `/root/local.rules` with a quoted heredoc. Use `http.method` `content:"POST"`, then `http.uri` `content:"/telemetry/v2/report"; startswith; endswith;`.
3. Add `http.header` `content:"X-TLM-Mode|3a| exfil|0d 0a|"`, then `http_client_body` with pcres `/(?:^|&)blob=[A-Za-z0-9+\/]{80,}={0,2}(?:&|$)/P` and `/(?:^|&)sig=[0-9a-fA-F]{64}(?:&|$)/P`. Finish with `sid:1000001; rev:1;`.
4. Validate with `suricata -T -S /root/local.rules`. Then run each pcap with `-k none -l` into a fresh directory, and count sid 1000001 in `eve.json` with jq: it must be present on positives and 0 on negatives.
