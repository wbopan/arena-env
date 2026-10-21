import json
import os
import random

random.seed(4242)
FIRST = ["Alex", "Priya", "Chen", "Maria", "Omar", "Lena", "Ravi", "Sofia", "Ken", "Ada", "Noah", "Iris"]
LAST = ["Kim", "Patel", "Wu", "Garcia", "Haddad", "Novak", "Rao", "Rossi", "Ito", "Berg", "Silva"]
emps = []
seen = set()
while len(emps) < 40:
    eid = "eid_%08x" % random.getrandbits(32)
    if eid in seen:
        continue
    seen.add(eid)
    emps.append({"employee_id": eid, "name": random.choice(FIRST) + " " + random.choice(LAST)})
EIDS = [e["employee_id"] for e in emps]
PRODUCTS = ["CoachForce", "CoFoAIX", "PitchPilot", "DealDesk"]
TARGET = "CoachForce"
docs = {p: [] for p in PRODUCTS}
meets = {p: [] for p in PRODUCTS}
used_dates = set()
state = {"n": 0, "m": 0}
FEEDBACK = [
    "Please add a competitor pricing comparison table.",
    "The TAM estimate needs a clearer source.",
    "Can we segment the survey results by company size?",
    "Section 3 should cite the latest analyst numbers.",
    "Add a risks paragraph about data privacy regulation.",
]
ACKS = ["Looks good to me.", "Thanks, nothing to add.", "Agreed.", "Sounds fine."]


def new_date():
    while True:
        d = "2025-%02d-%02d" % (random.randint(1, 12), random.randint(1, 28))
        if d not in used_dates:
            used_dates.add(d)
            return d


def add_doc(container, about, dtype, version, date=None):
    state["n"] += 1
    did = "doc_%04d" % ((state["n"] * 7919) % 10000)
    authors = random.sample(EIDS, random.choice([1, 2]))
    rest = [e for e in EIDS if e not in authors]
    reviewers = random.sample(rest, random.randint(0, 2))
    doc = {
        "id": did,
        "type": dtype,
        "title": f"{about} {dtype} {version}",
        "date": date or new_date(),
        "authors": authors,
        "reviewers": reviewers,
        "content": f"Draft {version} of the {dtype.lower()} for {about}. Audience: leadership. Status: in review.",
    }
    docs[container].append(doc)
    for _ in range(random.randint(1, 2)):
        state["m"] += 1
        parts = random.sample(rest, 6) + authors
        random.shuffle(parts)
        transcript = []
        for sp in parts:
            if random.random() < 0.45:
                transcript.append({"speaker": sp, "kind": "feedback", "text": random.choice(FEEDBACK)})
            else:
                transcript.append({"speaker": sp, "kind": "ack", "text": random.choice(ACKS)})
        meets[container].append({
            "id": f"{container}_review_{state['m']}",
            "doc_id": did,
            "participants": sorted(parts),
            "transcript": transcript,
        })
    return doc


for v in ["v1", "v2", "v3"]:
    add_doc(TARGET, TARGET, "Market Research Report", v)
add_doc(TARGET, "CoFoAIX", "Market Research Report", "v4", date="2025-12-30")
add_doc(TARGET, TARGET, "Product Requirements Document", "v1", date="2025-12-29")
add_doc(TARGET, TARGET, "Technical Spec", "v1")
add_doc("CoFoAIX", "CoFoAIX", "Market Research Report", "v1")
add_doc("CoFoAIX", "CoFoAIX", "Market Research Report", "v2")
add_doc("CoFoAIX", TARGET, "Market Research Report", "v5")
add_doc("CoFoAIX", "CoFoAIX", "Product Requirements Document", "v1")
for p in ["PitchPilot", "DealDesk"]:
    add_doc(p, p, "Market Research Report", "v1")
    add_doc(p, p, "Product Requirements Document", "v1")

os.makedirs(os.path.join("DATA", "products"), exist_ok=True)
for p in PRODUCTS:
    random.shuffle(docs[p])
    random.shuffle(meets[p])
    with open(os.path.join("DATA", "products", p + ".json"), "w", encoding="utf-8") as f:
        json.dump({"product": p, "documents": docs[p], "meetings": meets[p]}, f)
with open(os.path.join("DATA", "employees.json"), "w", encoding="utf-8") as f:
    json.dump(emps, f)
