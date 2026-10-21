#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json

def vt(x):
    return tuple(int(p) for p in x.split("."))

def sev(sc):
    if sc is None: return "UNKNOWN"
    if sc < 4.0: return "LOW"
    if sc < 7.0: return "MEDIUM"
    if sc < 9.0: return "HIGH"
    return "CRITICAL"

lock = json.load(open("package-lock.json"))
pairs = {(k.rsplit("node_modules/", 1)[1], m["version"]) for k, m in lock["packages"].items() if k}
advs = json.load(open("advisories.json"))["advisories"]
find = []
for name, ver in pairs:
    for a in advs:
        if a["package"] == name and any(vt(r["introduced"]) <= vt(ver) and (r["fixed"] is None or vt(ver) < vt(r["fixed"])) for r in a["ranges"]):
            sc = a["cvss_v3"] if a["cvss_v3"] is not None else a["cvss_v2"]
            find.append({"package": name, "version": ver, "advisory": a["id"], "score": sc, "severity": sev(sc)})
find.sort(key=lambda f: (f["package"], vt(f["version"]), f["advisory"]))
summary = {s: sum(1 for f in find if f["severity"] == s) for s in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]}
out = {"findings": find, "summary": summary, "affected_packages": len({f["package"] for f in find})}
json.dump(out, open("audit.json", "w"), indent=2)
EOF
python3 /tmp/solve.py
