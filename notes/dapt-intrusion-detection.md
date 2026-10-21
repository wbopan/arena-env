**Inputs and tools**
- The input is `/root/packets.pcap`. Read it with scapy: `from scapy.all import rdpcap, IP, TCP, UDP, ICMP, ARP`.
- A tested helper module lives at `/root/skills/pcap-analysis/pcap_utils.py`. Import it with `sys.path.insert(0,'/root/skills/pcap-analysis')`. It provides:
  - `load_packets`, `split_by_protocol` (returns a dict with keys such as `'ip'`, `'tcp'`, `'udp'`)
  - `graph_metrics`, `port_counters`, `ip_counters`, `iat_stats`, `flow_metrics`
  - `packets_per_minute_stats`, `producer_consumer_counts`, `shannon_entropy`
  - `detect_port_scan`, `detect_dos_pattern`, `detect_beaconing`
- Prefer these helpers. The skill says their edge cases and thresholds are the reference. Check their signatures and return keys cheaply first, without printing the whole file:
  - `grep -n "def \|return" /root/skills/pcap-analysis/pcap_utils.py | head -80`
- The output is `/root/network_stats.csv`, with header `metric,value`. Comment lines start with `#` and must be kept unchanged. Only fill the `value` column; keep metric names and their order. Inspect it with `cat /root/network_stats.csv` (it is small) to see the exact metric names.

**Definitions and formulas** (match the skill reference code)
- **Protocol counts:** count packets where `TCP in p`, `UDP in p`, `ICMP in p`, `ARP in p`. `protocol_ip_total` = packets with `IP in p`.
- **Sizes:** `len(p)` per packet. `total_bytes` is the sum; average, min and max are taken over all packets.
- **Duration:** `max(ts) - min(ts)`, using `ts = float(p.time)`.
- **Packets per minute:** bucket index = `int((ts - start)/60)`. Count packets per bucket, then take avg/max/min over the non-empty buckets that exist. The helper `packets_per_minute_stats` is the reference.
- **Entropy:** `H = -Σ p·log2 p` over a `Counter`.
  - IP entropy uses `IP.src`/`IP.dst` of IP packets.
  - Port entropy uses TCP and UDP sport/dport from packets that also have IP.
  - `unique_src_ports` / `unique_dst_ports` = `len(counter)`.
  - Use `ip_counters` / `port_counters` + `shannon_entropy` if available.
- **Graph** (from IP packets):
  - `edges` = set of (src, dst); nodes = all srcs ∪ dsts.
  - density = `E/(N*(N-1))`, or 0 if N<2.
  - `max_outdegree` = max size of the set of distinct destinations per source; `max_indegree` = max size of the set of distinct sources per destination.
  - These are counts of UNIQUE IPs, not packet counts (bounded by N−1).
- **IAT:** sort all packet timestamps and take consecutive differences.
  - `mean` = sum/len.
  - `variance` = population variance (divide by n, not n−1).
  - `cv = sqrt(var)/mean`, or 0 if mean = 0.
- **PCR:** over IP packets, `sent[src] += len(p)` and `recv[dst] += len(p)`. For each node, `pcr = (s-r)/(s+r)`.
  - pcr > 0.2 counts as a producer; pcr < −0.2 counts as a consumer.
- **Flows:** only packets with IP AND TCP/UDP.
  - Key = (src, dst, sport, dport, "TCP"/"UDP").
  - `unique_flows`, `tcp_flows`, `udp_flows` = set sizes.
  - **Pitfall in `bidirectional_flows`:** the skill code counts flows whose reverse key exists and then divides by 2 (counting pairs). Use whatever `flow_metrics()` returns, since that is the tested reference. Check its code with `grep -n -A30 "def flow_metrics" .../pcap_utils.py`.

**Detection flags** (exact thresholds; do not invent your own)
- **`has_port_scan`:** use `detect_port_scan(tcp_packets)`. It works per source with ≥50 TCP packets and requires ALL of:
  - dst-port entropy > 6.0
  - SYN-only ratio > 0.7 (SYN set: `flags & 0x02` and not ACK `0x10`)
  - unique dst ports > 100
- **`has_dos_pattern`:** use `detect_dos_pattern(ppm_avg, ppm_max)`. It is true only if max/avg > 20; it is false if avg = 0.
- **`has_beaconing`:** use `detect_beaconing(iat_cv)`, which is `iat_cv < 0.5`.
- **`is_traffic_benign`:** `not (scan or dos or beacon)`.
- Write flags as lowercase `true`/`false`, not Python `True`/`False`.

**Step-by-step plan**
1. Check the environment and inputs:
   - `ls /root /root/skills/*`
   - `cat /root/network_stats.csv`
   - `python3 -c "from scapy.all import rdpcap;p=rdpcap('/root/packets.pcap');print(len(p))"`
2. Grep `pcap_utils.py` for function signatures and return dict keys, as above.
3. Write `/root/solve.py`:
   ```python
   import sys, math, csv
   sys.path.insert(0,'/root/skills/pcap-analysis')
   from pcap_utils import *
   from scapy.all import IP, TCP, UDP, ICMP, ARP
   pk = load_packets('/root/packets.pcap'); parts = split_by_protocol(pk)
   R = {}
   # fill R from helpers (graph_metrics(parts['ip']), flow_metrics(...), iat_stats(...),
   # packets_per_minute_stats(...), producer_consumer_counts(...), ...);
   # compute anything missing manually per the definitions above
   # flags: R['has_port_scan'] = str(detect_port_scan(parts['tcp'])).lower(), etc.
   lines = open('/root/network_stats.csv').read().splitlines()
   out = []
   for ln in lines:
       if ln.startswith('#') or ln.strip()=='' or ln.split(',')[0]=='metric':
           out.append(ln); continue
       m = ln.split(',')[0]
       out.append(f"{m},{R.get(m, ln.split(',',1)[1] if ',' in ln else '')}")
   open('/root/network_stats.csv','w').write('\n'.join(out)+'\n')
   missing = [l.split(',')[0] for l in lines if not l.startswith('#') and l.split(',')[0] not in R and l.split(',')[0]!='metric']
   print('missing', missing)
   ```
   - Round floats to about 6 decimals or leave them unrounded; do not truncate to integers.
   - Integer metrics should be written as ints.
4. Run the script. Make sure `missing` is empty; any metric name in the template that is not in R must be computed.
5. Verify the output:
   - `grep -v '^#' /root/network_stats.csv | head -60`: every metric has a value and the flags are lowercase.
   - Sanity checks: max_indegree < num_nodes; ARP count + IP total ≈ total packets; ppm_max ≥ ppm_avg ≥ ppm_min.
   - The flags are consistent: benign is true only if all three other flags are false.
