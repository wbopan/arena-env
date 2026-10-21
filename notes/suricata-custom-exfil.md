**Goal.** Edit `/root/local.rules` so Suricata raises an alert with `sid:1000001` for true exfil HTTP requests and stays silent on the negative traffic. All five conditions must hold together:
- the method is POST;
- the path is exactly `/telemetry/v2/report`;
- a request header is `X-TLM-Mode: exfil`;
- the body has `blob=` followed by a Base64-looking value of at least 80 characters;
- the body has `sig=` followed by exactly 64 hex characters.

Keep the rule on one line in the file. Multi-line formatting needs a trailing `\` on each line, and `#` comments inside a rule break it. Keep `sid:1000001; rev:1;`. Do not add other rules that could fire on negatives.

**Tools**
- **tshark** – inspect the pcaps.
- **suricata** – run offline, including `-T` to test rule syntax.
- **jq** – read `eve.json`.

Never print whole pcaps or files. Use `head`, `-T fields`, and `cut -c`.

**Step 1: Cheap inspection** (about 6 commands)
```bash
ls -la /root/pcaps/; cat /root/local.rules; suricata -V
grep -n -A3 -i 'request-body-limit\|^ *http:' /root/suricata.yaml | head -30
for f in /root/pcaps/*.pcap; do echo == $f; tshark -r $f -Y http.request -T fields \
  -e http.request.method -e http.request.uri -e http.content_type -e http.content_length | sort | uniq -c | head; done
tshark -r /root/pcaps/train_pos.pcap -Y 'http.request.method=="POST"' -T fields -e http.file_data | head -3 | cut -c1-300
tshark -r /root/pcaps/train_neg.pcap -Y 'http.request.method=="POST"' -T fields -e http.file_data | cut -c1-300 | head -20
tshark -r /root/pcaps/train_neg.pcap -Y http.request -T fields -e http.request.line | grep -i tlm | head
```
What to learn from this:
- **Body encoding.** Is it form-urlencoded `a=b&c=d`? Is Base64 `+ / =` percent-encoded (`%2B`, `%2F`, `%3D`)? Is it base64url (`-` and `_`)?
- **Parameter order.** Does `sig` come before or after `blob`?
- **How the negatives differ.** Look for:
  - a GET to the same path;
  - a path with a suffix or a query, such as `/telemetry/v2/report?x=1`, `/telemetry/v2/reportX` or `/telemetry/v2/report/`;
  - header values like `X-TLM-Mode: exfil-test` or `normal`;
  - a blob of 79 characters or with non-Base64 characters;
  - a sig of 63 or 65 hex characters, or with non-hex characters;
  - `xsig=` or `myblob=` lookalike parameter names;
  - the parameters appearing only in a header or the URI.

If the body is large, make sure `request-body-limit` in the config is big enough. Otherwise `http_client_body` is truncated.

**Step 2: Rule building blocks** (Suricata 6/7 sticky-buffer syntax)

A sticky buffer applies to every `content` and `pcre` that follows it, until the next buffer keyword.

- **Method:** `http.method; content:"POST";`
  - A bare `content:"POST"` without the buffer can match inside the body.
- **Exact path:** `http.uri; content:"/telemetry/v2/report"; startswith; endswith;`
  - The alternative is `bsize:20;`; the path is 20 bytes.
  - `http.uri` includes the query string, so `startswith; endswith;` also rejects `?...` suffixes.
  - A pcre alternative is `pcre:"/^\/telemetry\/v2\/report$/U";`.
- **Header:** `http.header; content:"X-TLM-Mode|3a| exfil|0d 0a|";`
  - The `http.header` buffer holds lines of the form `Name: Value\r\n`.
  - The trailing `|0d 0a|` forces the value to be exactly `exfil`, not `exfil2`.
  - Write the colon as `|3a|`.
  - If the pcaps show varying case or spacing, use a pcre instead: `pcre:"/^X-TLM-Mode\x3a\s*exfil\r?$/miH";`.
- **Body:** use `http_client_body;` (or `http.request_body;`) before the body matches.
  - `content:"blob="; content:"sig=";` are fast prefilters.
  - `pcre:"/(?:^|&)blob=[A-Za-z0-9+\/]{80,}={0,2}(?:&|$)/P";`
  - `pcre:"/(?:^|&)sig=[0-9a-fA-F]{64}(?:&|$)/P";`
  - Each pcre is independent, so parameter order does not matter.
  - The `(?:^|&)` and `(?:&|$)` boundaries enforce exactly 64 hex characters and reject `xsig=`.
  - Without the end anchor, 65 hex characters would still match.
  - Adapt the character class to what you observed:
    - add `%` and hex digits if the body is percent-encoded, e.g. `(?:[A-Za-z0-9+\/]|%2[BbFf]|%3[Dd])`, though `{80,}` then counts tokens;
    - add `-_` only if base64url appears in the positives.
  - Keep the class strict. Do not use `.` or `\S`.
- **pcre flags:** `U` = normalized URI, `P` = client body, `H` = header, `i` = nocase, `m` = multiline. After a sticky buffer, a flag-less pcre also inspects that buffer.
- **Escaping:** inside `content` or `pcre` strings, escape `"` `;` `\` as `\"` `\;` `\\`, and write `/` inside a pcre as `\/`.
- **Header line:** `alert http any any -> any any (msg:"TLM exfil"; flow:established,to_server; ... sid:1000001; rev:1;)`

**Step 3: Write the rule.** Do this with a heredoc: `cat > /root/local.rules <<'EOF' ... EOF`. The quoted `'EOF'` stops the shell from expanding `$` and `\`.

**Step 4: Validate and test loop**
```bash
suricata -T -c /root/suricata.yaml -S /root/local.rules 2>&1 | tail -5
for f in /root/pcaps/*.pcap; do d=/tmp/suri-$(basename $f .pcap); rm -rf $d; mkdir -p $d
  suricata -c /root/suricata.yaml -S /root/local.rules -k none -r $f -l $d >/dev/null 2>&1
  echo "$f: $(jq -r 'select(.event_type=="alert")|.alert.signature_id' $d/eve.json | sort | uniq -c)"; done
```
- Use a fresh `-l` directory for each run.
- Check `suricata.log` (or stderr) for "error parsing signature".

**Step 5: Check the results**
- Positives should alert with sid 1000001; compare the alert count with the number of exfil POSTs found by tshark.
- Negatives should give 0 alerts.

**If the results are wrong**
- **A positive misses:**
  - dump that request's body or headers with `-e http.file_data` or `-x`;
  - check for chunked or gzip bodies, which Suricata dechunks;
  - check header case;
  - check the trailing `\r\n` versus the end of the buffer;
  - check percent-encoding.
- **A negative fires:** find which condition it violates and tighten that clause.

To see which request alerted, run `jq 'select(.event_type=="alert")|.http'`. Prefer the generalizable spec conditions over overfitting to specific training strings, because a hidden test pcap will be used.
