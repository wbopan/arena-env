import json
import os
import xml.etree.ElementTree as ET
from collections import deque

import pytest

W = '/root/work'
OUT = os.path.join(W, 'resolved.txt')
NS = {'m': 'http://maven.apache.org/POM/4.0.0'}


def expected():
    with open(os.path.join(W, 'repository.json')) as f:
        repo = json.load(f)
    root = ET.parse(os.path.join(W, 'pom.xml')).getroot()
    q = deque()
    for d in root.findall('m:dependencies/m:dependency', NS):
        g = d.find('m:groupId', NS).text.strip()
        a = d.find('m:artifactId', NS).text.strip()
        v = d.find('m:version', NS).text.strip()
        q.append((g + ':' + a, v, 1))
    res = {}
    while q:
        ga, v, depth = q.popleft()
        if ga in res:
            continue
        res[ga] = (v, depth)
        for e in repo[ga + ':' + v]:
            if e['optional']:
                continue
            g, a, vv = e['coord'].split(':')
            q.append((g + ':' + a, vv, depth + 1))
    return res


def read_lines():
    assert os.path.isfile(OUT), 'resolved.txt missing'
    with open(OUT) as f:
        return [l for l in f.read().splitlines()]


def parsed():
    out = {}
    for line in read_lines():
        coord, depth = line.split(' ')
        g, a, v = coord.split(':')
        out[g + ':' + a] = (v, int(depth))
    return out


def test_exists():
    assert os.path.isfile(OUT)


def test_format():
    lines = read_lines()
    assert lines
    for line in lines:
        parts = line.split(' ')
        assert len(parts) == 2, line
        assert parts[0].count(':') == 2, line
        assert parts[1].isdigit(), line


def test_sorted_unique():
    keys = [l.split(' ')[0].rsplit(':', 1)[0] for l in read_lines()]
    assert keys == sorted(keys)
    assert len(keys) == len(set(keys))


def test_artifact_set():
    assert set(parsed()) == set(expected())


def test_versions():
    got = parsed()
    for ga, (v, _) in expected().items():
        assert got.get(ga, (None, None))[0] == v, ga


def test_depths():
    got = parsed()
    for ga, (_, d) in expected().items():
        assert got.get(ga, (None, None))[1] == d, ga
