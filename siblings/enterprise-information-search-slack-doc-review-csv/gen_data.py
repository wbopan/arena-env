import csv
import json
import os
import random

random.seed(31337)
FIRST = ["Alex", "Priya", "Chen", "Maria", "Omar", "Lena", "Ravi", "Sofia"]
LAST = ["Kim", "Patel", "Wu", "Garcia", "Novak", "Rao"]
PRODUCTS = ["CoachForce", "PitchPilot", "DealDesk"]
SUBST = [
    "Please double check the churn numbers.",
    "Could we add a competitor pricing comparison section?",
    "The survey sample looks too small for enterprise buyers.",
    "I think the rollout timeline in section two is optimistic.",
    "Can we split the TAM estimate by region please?",
]
ACK = ["LGTM", "Looks good, thanks!", "Great work on this one", "Nice, approved.", "Thanks for sharing this"]
CHATTER = [
    "Standup moved to 10am tomorrow.",
    "Reminder: notes live in the docs folder.",
    "Who owns the Q3 roadmap deck?",
    "Wiki page: https://wiki.example.com/archives/wiki/onboarding",
]

team = {}
for p in PRODUCTS:
    names = set()
    while len(names) < 8:
        names.add(random.choice(FIRST) + " " + random.choice(LAST))
    team[p] = sorted(names)
shared = team["CoachForce"][0]
for p in PRODUCTS[1:]:
    if shared not in team[p]:
        team[p][0] = shared

used = set()


def new_eid():
    while True:
        e = "eid_%08x" % random.getrandbits(32)
        if e not in used:
            used.add(e)
            return e


emps = [{"employee_id": new_eid(), "name": n, "team": p} for p in PRODUCTS for n in team[p]]
random.shuffle(emps)
docs_used = set()


def new_doc():
    while True:
        d = "doc_%06x" % random.getrandbits(24)
        if d not in docs_used:
            docs_used.add(d)
            return d


msgs = []


def post(channel, user, text, parent=None):
    mid = "m%04d" % (len(msgs) + 1)
    msgs.append({"id": mid, "channel": channel, "ts": 1700000000 + 137 * len(msgs),
                 "user_name": user, "text": text, "parent_id": parent})
    return mid


def reply_text():
    x = random.random()
    if x < 0.1:
        return "See also https://wiki.example.com/archives/docs/%s for last quarter context." % new_doc()
    if x < 0.55:
        return random.choice(SUBST)
    return random.choice(ACK)


for p in PRODUCTS:
    for ch, n in ((f"planning-{p}", 4), (f"eng-{p}", 2)):
        for _ in range(n):
            sharer = random.choice(team[p])
            top = post(ch, sharer, "Here is the latest draft for review: https://wiki.example.com/archives/docs/" + new_doc())
            for _ in range(random.randint(0, 4)):
                post(ch, random.choice(team[p]), reply_text(), top)
    for _ in range(3):
        top = post(f"planning-{p}", random.choice(team[p]), random.choice(CHATTER))
        for _ in range(random.randint(0, 2)):
            post(f"planning-{p}", random.choice(team[p]), reply_text(), top)
random.shuffle(msgs)

os.makedirs("DATA", exist_ok=True)
with open(os.path.join("DATA", "slack.json"), "w", encoding="utf-8") as f:
    json.dump(msgs, f)
with open(os.path.join("DATA", "employees.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["employee_id", "name", "team"])
    w.writeheader()
    w.writerows(emps)
