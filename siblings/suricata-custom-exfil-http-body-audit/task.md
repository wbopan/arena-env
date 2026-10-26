An HTTP capture was exported as individual request records rather than as packets. Audit it for the custom telemetry exfiltration pattern.

Input: `/root/work/requests.jsonl`. Each line is a JSON object with an integer `id` and a `request` string containing one complete HTTP/1.1 request. The request uses CRLF line endings. Its body is the text after the first blank line; do not search the request line or headers for body parameters.

A request qualifies only if its method is `POST`, its path is exactly `/telemetry/v2/report`, and it has a header named `X-TLM-Mode` whose trimmed value is `exfil`. Header names are case-insensitive. The body uses URL-form-style `&`-separated parameters. It must contain a `blob` value consisting entirely of at least 80 Base64 alphabet characters (`A-Z`, `a-z`, `0-9`, `+`, `/`, or `=`), and a `sig` value consisting of exactly 64 hexadecimal characters. Parameter names and values are case-sensitive.

Write `/root/work/qualified.json` as a JSON array sorted by ascending `id`. Include only qualifying requests. Each object must have exactly `id` (integer), `blob_chars` (integer character count), and `sig_prefix` (the first eight characters of `sig`, preserving case). An empty result is `[]`.
