#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import re
sizes = {"char": 1, "unsigned char": 1, "short": 2, "unsigned short": 2, "int": 4,
         "unsigned int": 4, "long": 8, "unsigned long": 8, "long long": 8}
src = open("zq.h").read()
src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
structs = {}
for name, body in re.findall(r"struct\s+(\w+)\s*\{(.*?)\};", src, re.S):
    off = 0; maxa = 1
    for fld in [x.strip() for x in body.split(";") if x.strip()]:
        s = sizes[" ".join(fld.split()[:-1])]
        if off % s:
            off += s - off % s
        off += s; maxa = max(maxa, s)
    if off % maxa:
        off += maxa - off % maxa
    structs[name] = off
defs = []
for line in src.splitlines():
    p = line.strip().split(None, 2)
    if len(p) == 3 and p[0] == "#define":
        defs.append((p[1], p[2].strip()))
chars = {n: ord(v[1]) for n, v in defs if len(v) == 3 and v[0] == v[2] == "'"}
out = {}
dirs = {"_IO": 0, "_IOW": 1, "_IOR": 2, "_IOWR": 3}
for n, v in defs:
    if n in chars:
        continue
    m = re.match(r"(_IO\w*)\((.*)\)$", v)
    if m:
        args = [a.strip() for a in m.group(2).split(",")]
        t = chars[args[0]] if args[0] in chars else ord(args[0][1])
        nr = int(args[1], 16)
        size = 0
        if len(args) > 2:
            a = " ".join(args[2].split())
            size = structs[a[7:]] if a.startswith("struct ") else sizes[a]
        out[n] = (dirs[m.group(1)] << 30) | (size << 16) | (t << 8) | nr
    elif "<<" in v:
        out[n] = 1 << int(v.strip("() ").split("<<")[1])
    else:
        out[n] = int(v, 0)
with open("dev_zq.txt.const", "w") as f:
    f.write("arches = amd64\n")
    for n in sorted(out):
        f.write(f"{n} = {out[n]}\n")
EOF
python3 /tmp/solve.py
