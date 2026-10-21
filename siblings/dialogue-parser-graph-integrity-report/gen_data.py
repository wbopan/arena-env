import json
import random

random.seed(11)
PRE = ["Gate", "Bribe", "Duel", "Tavern", "Oath", "Secret", "Escape", "Trial", "Feast", "Ambush"]
N = 34
ids = ["Intro"] + [random.choice(PRE) + str(i) for i in range(1, N)]
nodes, edges = [], []
for i, nid in enumerate(ids):
    typ = "choice" if random.random() < 0.45 else "line"
    nodes.append({"id": nid, "text": "" if typ == "choice" else "Line %d" % i,
                  "speaker": "" if typ == "choice" else random.choice(["Guard", "Mira", "Vex"]), "type": typ})
    if i > 0 and random.random() < 0.12:
        k = 0
    elif typ == "choice":
        k = random.randint(2, 4)
    else:
        k = 1
    for j in range(k):
        r = random.random()
        if r < 0.12 or i >= N - 2:
            t = "End"
        elif r < 0.2:
            t = "Missing%d" % random.randint(1, 5)
        else:
            t = ids[random.randint(i + 1, min(N - 1, i + 7))]
        edges.append({"from": nid, "to": t, "text": ("%d. option" % (j + 1)) if typ == "choice" else ""})
rest = nodes[1:]
random.shuffle(rest)
random.shuffle(edges)
with open("dialogue.json", "w") as f:
    json.dump({"nodes": [nodes[0]] + rest, "edges": edges}, f, indent=1)
