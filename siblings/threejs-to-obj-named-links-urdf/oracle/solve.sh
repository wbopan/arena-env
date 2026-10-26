#!/usr/bin/env bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_links.py <<'PY'
import json
import xml.etree.ElementTree as ET

scene = json.load(open('/root/work/scene.json'))
parts = {}
def walk(node, parent=None):
    if node['type'] == 'Group' and node['name']:
        parts[node['name']] = {'parent': parent, 'motion': node['motion'], 'count': 0}
        parent = node['name']
    if node['type'] == 'Mesh' and parent is not None:
        parts[parent]['count'] += 1
    for child in node['children']:
        walk(child, parent)
walk(scene['root'])
parts = {name: data for name, data in parts.items() if data['count']}
robot = ET.Element('robot', {'name': 'assembly'})
for name in sorted(parts):
    link = ET.SubElement(robot, 'link', {'name': name})
    visual = ET.SubElement(link, 'visual')
    geometry = ET.SubElement(visual, 'geometry')
    ET.SubElement(geometry, 'mesh', {'filename': 'meshes/' + name + '.obj'})
for name in sorted(parts):
    data = parts[name]
    if data['parent'] is None:
        continue
    joint = ET.SubElement(robot, 'joint', {'name': 'joint_' + name, 'type': data['motion']})
    ET.SubElement(joint, 'parent', {'link': data['parent']})
    ET.SubElement(joint, 'child', {'link': name})
ET.ElementTree(robot).write('/root/work/assembly.urdf', encoding='utf-8', xml_declaration=True)
PY
python /tmp/solve_links.py
