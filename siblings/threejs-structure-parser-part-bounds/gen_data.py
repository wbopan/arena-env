import json
import math
import random

random.seed(9062)

def matrix(tx, ty, tz, degrees, scale):
    a = math.radians(degrees)
    c, s = math.cos(a) * scale, math.sin(a) * scale
    return [c, s, 0, 0, -s, c, 0, 0, 0, 0, scale, 0, tx, ty, tz, 1]

def node(kind, name, children=None):
    result = {'type': kind, 'name': name, 'matrix': matrix(*(round(random.uniform(-3, 3), 3) for _ in range(3)), random.choice([-45, -20, 15, 40]), random.choice([0.75, 1.0, 1.25]))}
    if children is not None:
        result['children'] = children
    return result

def mesh(name):
    result = node('Mesh', name)
    result['positions'] = [round(random.uniform(-1.5, 1.5), 3) for _ in range(3 * random.choice([4, 5, 6]))]
    return result

root = node('Scene', 'root', [
    node('Group', 'frame', [mesh('rail'), node('Group', '', [mesh('brace'), node('Group', 'dial', [mesh('face')])])]),
    node('Object3D', 'wrapper', [node('Group', 'cover', [mesh('shell'), mesh('lip')])]),
    node('Group', 'empty', [node('Group', 'pin', [mesh('shaft')])]),
])
random.shuffle(root['children'])
with open('scene.json', 'w') as f:
    json.dump({'object': root}, f, indent=2)
