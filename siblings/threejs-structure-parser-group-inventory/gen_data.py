import json
import random

random.seed(7341)

def mesh(i):
    return {'type': 'Mesh', 'name': f'mesh_{i:02d}', 'geometry': f'geo_{random.randrange(100, 999)}'}

def group(name, children):
    return {'type': 'Group', 'name': name, 'children': children}

names = ['base', 'arm', 'tip', 'guard', 'socket', 'cap']
random.shuffle(names)
n = iter(range(30))
scene = {'type': 'Scene', 'name': 'assembly', 'children': [
    mesh(next(n)),
    group(names[0], [mesh(next(n)), group('', [mesh(next(n)), group(names[1], [mesh(next(n)), mesh(next(n))])])]),
    {'type': 'Object3D', 'name': 'spacer', 'children': [group(names[2], [group(names[3], [mesh(next(n))]), mesh(next(n))])]},
    group(names[4], []),
    group('', [mesh(next(n)), group(names[5], [mesh(next(n))])]),
]}
random.shuffle(scene['children'])
with open('scene.json', 'w') as f:
    json.dump({'metadata': {'type': 'Object'}, 'object': scene}, f, indent=2)
