#!/bin/bash
set -e
cd /root/work
cat > /tmp/audit.py <<'EOF'
import os, json
SRC = "/root/work/src"
PKGS = ["javax.persistence", "javax.validation", "javax.servlet", "javax.transaction",
        "javax.ws.rs", "javax.mail", "javax.jms", "javax.xml.bind"]
ANN = {"PostConstruct", "PreDestroy", "Resource", "Priority"}

def target(n):
    if n.startswith("javax.transaction.xa."):
        return None
    for p in PKGS:
        if n.startswith(p + "."):
            return "jakarta" + p[len("javax"):]
    if n.startswith("javax.annotation.") and n[len("javax.annotation."):] in ANN:
        return "jakarta.annotation"
    return None

scanned = 0
per = {}
bypkg = {}
kept = set()
for root, dirs, files in os.walk(SRC):
    for f in files:
        if not f.endswith(".java"):
            continue
        scanned += 1
        p = os.path.join(root, f)
        rel = os.path.relpath(p, SRC).replace(os.sep, "/")
        c = 0
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                s = line.strip()
                if not s.startswith("import "):
                    continue
                n = s[7:].strip()
                if n.startswith("static "):
                    n = n[7:].strip()
                n = n.split(";")[0].strip()
                t = target(n)
                if t:
                    c += 1
                    bypkg[t] = bypkg.get(t, 0) + 1
                elif n.startswith("javax."):
                    kept.add(n)
        if c:
            per[rel] = c
out = {
    "files_scanned": scanned,
    "files_changed": len(per),
    "total_migrated_imports": sum(per.values()),
    "by_package": bypkg,
    "per_file": per,
    "retained_javax": sorted(kept),
}
with open("/root/work/migration_report.json", "w") as f:
    json.dump(out, f, indent=2)
EOF
python3 /tmp/audit.py
