#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json, re, struct
B64 = re.compile(r"[A-Za-z0-9+/]+={0,2}")
HX = re.compile(r"[0-9a-fA-F]{64}")
data = open("/root/work/traffic.pcap", "rb").read()
pos = 24
idx = 0
alerts = []
while pos + 16 <= len(data):
    incl = struct.unpack("<IIII", data[pos:pos+16])[2]
    pos += 16
    fr = data[pos:pos+incl]
    pos += incl
    idx += 1
    if fr[12:14] != b"\x08\x00":
        continue
    ip = fr[14:]
    if ip[9] != 6:
        continue
    ihl = (ip[0] & 15) * 4
    tot = struct.unpack("!H", ip[2:4])[0]
    tcp = ip[ihl:tot]
    pl = tcp[(tcp[12] >> 4) * 4:]
    if b"\r\n\r\n" not in pl:
        continue
    h, body = pl.decode("latin-1").split("\r\n\r\n", 1)
    lines = h.split("\r\n")
    rl = lines[0].split(" ")
    if len(rl) != 3 or rl[0] != "POST" or rl[1] != "/telemetry/v2/report":
        continue
    if not any(":" in l and l.split(":", 1)[0].strip().lower() == "x-tlm-mode" and l.split(":", 1)[1].strip() == "exfil" for l in lines[1:]):
        continue
    kv = {}
    for p in body.split("&"):
        if "=" in p:
            k, v = p.split("=", 1)
            kv.setdefault(k, v)
    b, s = kv.get("blob"), kv.get("sig")
    if b is None or s is None or len(b) < 80 or not B64.fullmatch(b) or not HX.fullmatch(s):
        continue
    src = ".".join(map(str, ip[12:16])) + ":" + str(struct.unpack("!H", tcp[0:2])[0])
    alerts.append({"packet": idx, "src": src})
alerts.sort(key=lambda a: a["packet"])
json.dump({"count": len(alerts), "alerts": alerts}, open("/root/work/alerts.json", "w"), indent=2)
EOF
python3 /tmp/solve.py
