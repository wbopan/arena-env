import json
from pathlib import Path
import xml.etree.ElementTree as ET

BASE = Path('/root/work')
OUT = BASE / 'assembly.urdf'

def model():
    root = json.loads((BASE / 'scene.json').read_text())['root']
    links = {}
    def visit(node, owner=None):
        if node['type'] == 'Group' and node['name']:
            links[node['name']] = {'parent': owner, 'motion': node['motion'], 'meshes': []}
            owner = node['name']
        if node['type'] == 'Mesh' and owner is not None:
            links[owner]['meshes'].append(node['geometry'])
        for child in node['children']:
            visit(child, owner)
    visit(root)
    return {k: v for k, v in links.items() if v['meshes']}

def xml():
    return ET.parse(OUT).getroot()

def test_file_exists():
    assert OUT.is_file() and OUT.stat().st_size > 0

def test_robot_and_element_schema():
    r = xml()
    assert r.tag == 'robot' and r.attrib == {'name': 'assembly'}
    assert all(child.tag in ('link', 'joint') for child in r)
    assert all(not link.findall('./inertial') for link in r.findall('link'))

def test_links_and_mesh_references():
    r, names = xml(), sorted(model())
    links = r.findall('link')
    assert [link.get('name') for link in links] == names
    for link in links:
        assert len(list(link)) == 1
        assert len(link.findall('./visual/geometry/mesh')) == 1
        assert link.find('./visual/geometry/mesh').attrib == {'filename': f"meshes/{link.get('name')}.obj"}

def test_joint_names_order_and_types():
    r, links = xml(), model()
    children = sorted(name for name, data in links.items() if data['parent'] is not None)
    joints = r.findall('joint')
    assert [j.get('name') for j in joints] == ['joint_' + n for n in children]
    assert [j.get('type') for j in joints] == [links[n]['motion'] for n in children]

def test_joint_parent_child_and_order():
    r, links = xml(), model()
    assert [e.tag for e in r] == ['link'] * len(links) + ['joint'] * (len(links) - 1)
    for joint in r.findall('joint'):
        child = joint.get('name')[6:]
        assert [e.tag for e in joint] == ['parent', 'child']
        assert joint.find('parent').attrib == {'link': links[child]['parent']}
        assert joint.find('child').attrib == {'link': child}
