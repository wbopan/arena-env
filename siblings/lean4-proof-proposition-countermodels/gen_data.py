import json
import random

random.seed(3098)
variables = ['a', 'b', 'c', 'd']
def atom():
    return {'var': random.choice(variables)}
def tree(depth):
    if depth == 0 or random.random() < 0.25:
        return atom()
    if random.random() < 0.25:
        return {'not': tree(depth - 1)}
    op = random.choice(['and', 'or', 'imp'])
    return {op: [tree(depth - 1), tree(depth - 1)]}

claims = []
for i in range(18):
    if i % 3 == 0:
        part = tree(2)
        formula = {'imp': [part, part]}
    elif i % 3 == 1:
        part = tree(2)
        formula = {'and': [part, {'not': part}]}
    else:
        formula = tree(3)
    claims.append({'id': f'C{i:02d}', 'formula': formula})
with open('claims.json', 'w', encoding='utf-8') as stream:
    json.dump(claims, stream, indent=2)
