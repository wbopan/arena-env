#!/bin/bash
set -e
cd /root/work
cat > /tmp/migrate_pom.py <<'EOF'
import xml.etree.ElementTree as ET
NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)
q = lambda t: "{%s}%s" % (NS, t)
REMOVE = {("javax.xml.bind", "jaxb-api"), ("com.sun.xml.bind", "jaxb-impl"),
          ("com.sun.xml.bind", "jaxb-core"), ("javax.activation", "activation"),
          ("javax.activation", "javax.activation-api")}
REN = {("javax.servlet", "javax.servlet-api"): ("jakarta.servlet", "jakarta.servlet-api"),
       ("javax.validation", "validation-api"): ("jakarta.validation", "jakarta.validation-api"),
       ("javax.persistence", "javax.persistence-api"): ("jakarta.persistence", "jakarta.persistence-api"),
       ("javax.annotation", "javax.annotation-api"): ("jakarta.annotation", "jakarta.annotation-api")}
tree = ET.parse("pom.xml")
r = tree.getroot()
r.find(q("parent")).find(q("version")).text = "3.2.0"
r.find(q("properties")).find(q("java.version")).text = "21"
deps = r.find(q("dependencies"))
old = list(deps)
for c in old:
    deps.remove(c)
def mk(g, a, v=None, s=None):
    d = ET.SubElement(deps, q("dependency"))
    for tag, val in (("groupId", g), ("artifactId", a), ("version", v), ("scope", s)):
        if val:
            ET.SubElement(d, q(tag)).text = val
def get(d, t):
    v = d.findtext(q(t))
    return v.strip() if v and v.strip() else None
for d in old:
    if d.tag != q("dependency"):
        continue
    g, a, v, s = get(d, "groupId"), get(d, "artifactId"), get(d, "version"), get(d, "scope")
    if (g, a) in REMOVE:
        continue
    if (g, a) == ("io.jsonwebtoken", "jjwt"):
        mk("io.jsonwebtoken", "jjwt-api", "0.12.3")
        mk("io.jsonwebtoken", "jjwt-impl", "0.12.3", "runtime")
        mk("io.jsonwebtoken", "jjwt-jackson", "0.12.3", "runtime")
    elif (g, a) in REN:
        ng, na = REN[(g, a)]
        mk(ng, na, None, s)
    else:
        mk(g, a, v, s)
tree.write("pom-migrated.xml", xml_declaration=True, encoding="UTF-8")
EOF
python3 /tmp/migrate_pom.py
