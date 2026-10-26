import json
import random

random.seed(625)
names = [f'{stem}_{random.randrange(100, 999)}' for stem in ('frame', 'lever', 'tool', 'carriage')]
def mesh(key):
    return {'type': 'Mesh', 'name': '', 'geometry': key, 'children': []}
def group(name, motion, children):
    return {'type': 'Group', 'name': name, 'motion': motion, 'children': children}
def wrapper(children):
    return {'type': 'Group', 'name': '', 'children': children}
tool = group(names[2], 'fixed', [mesh('cap'), mesh('pin')])
lever = group(names[1], 'revolute', [mesh('bar'), wrapper([tool])])
carriage = group(names[3], 'prismatic', [wrapper([mesh('rail')])])
frame = group(names[0], 'fixed', [wrapper([mesh('plate')]), lever, carriage])
root = {'type': 'Scene', 'name': '', 'children': [frame, wrapper([mesh('unowned')])]}
with open('scene.json', 'w') as f:
    json.dump({'root': root}, f, indent=2)
