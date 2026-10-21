import json
import os
import re
import xml.etree.ElementTree as ET

import pytest

W = '/root/work'
OUT = os.path.join(W, 'effective-deps.json')
NS = {'m': 'http://maven.apache.org/POM/4.0.0'}
PAT = re.compile(r'[$][{]([^}]*)[}]')


def t(el, path):
    e = el.find(path, NS)
    if e is None or e.text is None:
        return None
    return e.text.strip()


def props_of(root):
    p = {}
    pe = root.find('m:properties', NS)
    if pe is not None:
        for c in pe:
            p[c.tag.split('}')[-1]] = (c.text or '').strip()
    return p


def interp(s, props):
    for _ in range(100):
        n = PAT.sub(lambda m: props[m.group(1)], s)
        if n == s:
            break
        s = n
    return s


def expected():
    parent = ET.parse(os.path.join(W, 'pom.xml')).getroot()
    pprops = props_of(parent)
    pver = t(parent, 'm:version')
    managed = {}
    for d in parent.findall('m:dependencyManagement/m:dependencies/m:dependency', NS):
        managed[(t(d, 'm:groupId'), t(d, 'm:artifactId'))] = (t(d, 'm:version'), t(d, 'm:scope'))
    res = {}
    for me in parent.findall('m:modules/m:module', NS):
        root = ET.parse(os.path.join(W, me.text.strip(), 'pom.xml')).getroot()
        props = dict(pprops)
        props.update(props_of(root))
        props['project.version'] = t(root, 'm:version') or pver
        lst = []
        for d in root.findall('m:dependencies/m:dependency', NS):
            g, a = t(d, 'm:groupId'), t(d, 'm:artifactId')
            mv, ms = managed.get((g, a), (None, None))
            v = t(d, 'm:version') or mv
            s = t(d, 'm:scope') or ms or 'compile'
            lst.append({'groupId': g, 'artifactId': a, 'version': interp(v, props), 'scope': s})
        res[t(root, 'm:artifactId')] = lst
    return res


@pytest.fixture(scope='module')
def out():
    assert os.path.isfile(OUT), 'effective-deps.json missing'
    with open(OUT) as f:
        return json.load(f)


@pytest.fixture(scope='module')
def exp():
    return expected()


def test_file_is_json_object(out):
    assert isinstance(out, dict)


def test_schema(out):
    for mod, lst in out.items():
        assert isinstance(lst, list), mod
        for e in lst:
            assert isinstance(e, dict)
            assert set(e.keys()) == {'groupId', 'artifactId', 'version', 'scope'}, e
            assert all(isinstance(x, str) for x in e.values()), e


def test_module_keys(out, exp):
    assert set(out.keys()) == set(exp.keys())


def test_dependency_order(out, exp):
    for mod, lst in exp.items():
        got = [(e['groupId'], e['artifactId']) for e in out.get(mod, [])]
        assert got == [(e['groupId'], e['artifactId']) for e in lst], mod


def test_versions(out, exp):
    for mod, lst in exp.items():
        got = {(e['groupId'], e['artifactId']): e['version'] for e in out.get(mod, [])}
        for e in lst:
            assert got.get((e['groupId'], e['artifactId'])) == e['version'], (mod, e)


def test_scopes(out, exp):
    for mod, lst in exp.items():
        got = {(e['groupId'], e['artifactId']): e['scope'] for e in out.get(mod, [])}
        for e in lst:
            assert got.get((e['groupId'], e['artifactId'])) == e['scope'], (mod, e)
