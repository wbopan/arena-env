import json
import random

random.seed(20240611)
NB = 12
nums = sorted(random.sample(range(1, 400), NB))
order = nums[:]
random.shuffle(order)
slack = order[0]
gen_buses = [slack] + order[1:4]

buses = []
for n in nums:
    if n == slack:
        t = 3
    elif n in gen_buses:
        t = 2
    else:
        t = 1
    if n in gen_buses and random.random() < 0.5:
        pd = 0.0
    else:
        pd = round(random.uniform(10, 60), 1)
    buses.append([n, t, pd, round(pd * 0.3, 1), 0, 0, 1, 1.0, 0, 138, 1, 1.06, 0.94])

pairs = set()
branches = []


def add_branch(a, b, status):
    x = round(random.uniform(0.02, 0.25), 4)
    r = round(x * 0.1, 4)
    rate = float(random.randint(40, 250))
    branches.append([a, b, r, x, 0.02, rate, rate, rate, 0, 0, status, -360, 360])
    pairs.add(frozenset((a, b)))


for i in range(1, NB):
    j = random.randrange(i)
    add_branch(order[i], order[j], 1)
extra = 0
while extra < 6:
    a, b = random.sample(nums, 2)
    if frozenset((a, b)) in pairs:
        continue
    add_branch(a, b, 0 if extra < 2 else 1)
    extra += 1
random.shuffle(branches)

total = sum(b[2] for b in buses)
others = []
for gb in gen_buses[1:]:
    others.append([gb, round(random.uniform(0.12, 0.22) * total, 1)])
slack_pg = round(total - sum(p for _, p in others), 3)
gens = []
for gb, pg in [[slack, slack_pg]] + others:
    gens.append([gb, pg, 0, 100, -100, 1.0, 100, 1, 400, 0])

data = {"baseMVA": 100.0, "bus": buses, "gen": gens, "branch": branches}
with open("network.json", "w") as f:
    json.dump(data, f, indent=1)
