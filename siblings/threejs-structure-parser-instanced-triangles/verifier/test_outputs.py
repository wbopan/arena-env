import json
from pathlib import Path

INPUT = Path('/root/work/instances.json')
OUTPUT = Path('/root/work/expanded.obj')

def apply(m, v):
    x, y, z = v
    return tuple(sum(m[4 * j + i] * (x, y, z, 1)[j] for j in range(4)) for i in range(3))

def expected():
    data = json.loads(INPUT.read_text())
    p = data['geometry']['positions']
    local = [p[i:i + 3] for i in range(0, len(p), 3)]
    ix = data['geometry']['indices']
    vertices, faces = [], []
    for instance in data['instance_matrices']:
        offset = len(vertices)
        vertices.extend(apply(data['mesh_matrix'], apply(instance, v)) for v in local)
        faces.extend(tuple(offset + ix[j + k] + 1 for k in range(3)) for j in range(0, len(ix), 3))
    return vertices, faces

def parsed():
    vertices, faces, other = [], [], []
    for line in OUTPUT.read_text().splitlines():
        fields = line.split()
        if not fields or fields[0].startswith('#'):
            continue
        if fields[0] == 'v':
            assert len(fields) == 4
            vertices.append(tuple(map(float, fields[1:])))
        elif fields[0] == 'f':
            assert len(fields) == 4
            faces.append(tuple(map(int, fields[1:])))
        else:
            other.append(fields[0])
    return vertices, faces, other

def test_file_exists():
    assert OUTPUT.is_file()

def test_record_types_and_counts():
    vertices, faces, other = parsed()
    ev, ef = expected()
    assert not other
    assert len(vertices) == len(ev) and len(faces) == len(ef)

def test_world_vertices():
    vertices, _, _ = parsed()
    ev, _ = expected()
    assert all(abs(a - b) <= 0.0000006 for v, w in zip(vertices, ev) for a, b in zip(v, w))

def test_triangle_indices():
    _, faces, _ = parsed()
    assert faces == expected()[1]
