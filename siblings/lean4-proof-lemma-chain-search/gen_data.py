import csv
import random

random.seed(7712)
nodes = [f'P{i:02d}' for i in range(20)]
edges = {(nodes[i], nodes[i + 1]) for i in range(14)}
for _ in range(55):
    a = random.randrange(19)
    b = random.randrange(19)
    if a != b:
        edges.add((nodes[a], nodes[b]))
edges.update({('P00', 'P02'), ('P00', 'P03'), ('P02', 'P05'), ('P03', 'P05')})
with open('lemmas.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['premise', 'conclusion'])
    writer.writerows(sorted(edges))
goals = []
for i in range(14):
    goals.append([f'G{i:02d}', random.choice(nodes), random.choice(nodes)])
goals.extend([['G14', 'P00', 'P05'], ['G15', 'P04', 'P04'],
              ['G16', 'P19', 'P00'], ['G17', 'P00', 'P19']])
with open('goals.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['goal_id', 'known', 'target'])
    writer.writerows(goals)
