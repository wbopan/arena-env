import json
from pathlib import Path

INPUT = Path('/root/work/scene.json')
OUTPUT = Path('/root/work/group_inventory.json')

def expected():
    root = json.loads(INPUT.read_text())['object']
    groups = {}
    unowned = []
    def visit(node, owner):
        if node['type'] == 'Group' and node.get('name'):
            name = node['name']
            groups[name] = {'name': name, 'parent': owner, 'meshes': []}
            owner = name
        if node['type'] == 'Mesh':
            (groups[owner]['meshes'] if owner is not None else unowned).append(node['name'])
        for child in node.get('children', []):
            visit(child, owner)
    visit(root, None)
    for item in groups.values():
        item['meshes'].sort()
    return {'groups': [groups[k] for k in sorted(groups)], 'unowned_meshes': sorted(unowned)}

def result():
    return json.loads(OUTPUT.read_text())

def test_file_exists():
    assert OUTPUT.is_file()

def test_schema():
    data = result()
    assert set(data) == {'groups', 'unowned_meshes'}
    assert isinstance(data['groups'], list) and isinstance(data['unowned_meshes'], list)
    assert all(set(g) == {'name', 'parent', 'meshes'} for g in data['groups'])

def test_group_names_and_parents():
    got, want = result(), expected()
    assert [(g['name'], g['parent']) for g in got['groups']] == [(g['name'], g['parent']) for g in want['groups']]

def test_mesh_ownership():
    got, want = result(), expected()
    assert [g['meshes'] for g in got['groups']] == [g['meshes'] for g in want['groups']]
    assert got['unowned_meshes'] == want['unowned_meshes']
