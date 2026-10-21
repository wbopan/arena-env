#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_effdeps.py <<'EOF'
import json, os, re
import xml.etree.ElementTree as ET
NS = {'m': 'http://maven.apache.org/POM/4.0.0'}
PAT = re.compile(r'[$][{]([^}]*)[}]')

def t(el, path):
    e = el.find(path, NS)
    return None if e is None or e.text is None else e.text.strip()

def props_of(root):
    pe = root.find('m:properties', NS)
    return {} if pe is None else {c.tag.split('}')[-1]: (c.text or '').strip() for c in pe}

def interp(s, props):
    while True:
        n = PAT.sub(lambda m: props[m.group(1)], s)
        if n == s:
            return s
        s = n

parent = ET.parse('pom.xml').getroot()
pprops = props_of(parent)
pver = t(parent, 'm:version')
managed = {(t(d, 'm:groupId'), t(d, 'm:artifactId')): (t(d, 'm:version'), t(d, 'm:scope'))
           for d in parent.findall('m:dependencyManagement/m:dependencies/m:dependency', NS)}
res = {}
for me in parent.findall('m:modules/m:module', NS):
    root = ET.parse(os.path.join(me.text.strip(), 'pom.xml')).getroot()
    props = dict(pprops)
    props.update(props_of(root))
    props['project.version'] = t(root, 'm:version') or pver
    lst = []
    for d in root.findall('m:dependencies/m:dependency', NS):
        g, a = t(d, 'm:groupId'), t(d, 'm:artifactId')
        mv, ms = managed.get((g, a), (None, None))
        lst.append({'groupId': g, 'artifactId': a,
                    'version': interp(t(d, 'm:version') or mv, props),
                    'scope': t(d, 'm:scope') or ms or 'compile'})
    res[t(root, 'm:artifactId')] = lst
with open('effective-deps.json', 'w') as f:
    json.dump(res, f, indent=2)
EOF
python3 /tmp/solve_effdeps.py
