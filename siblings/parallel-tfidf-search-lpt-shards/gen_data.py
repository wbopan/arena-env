import json
import random

random.seed(777)

VOCAB = ["index", "search", "query", "vector", "worker", "thread", "process", "memory",
         "cache", "shard", "token", "corpus", "score", "rank", "weight", "term",
         "engine", "parallel", "chunk", "queue", "merge", "reduce", "latency", "core",
         "pool", "sparse", "hash", "heap", "batch", "stream", "buffer", "lock",
         "kernel", "balance", "split", "join", "filter", "data", "base", "node"]
PUNCT = ["", "", "", ",", ".", ";", ":", "!"]


def piece():
    r = random.random()
    if r < 0.08:
        w = random.choice(VOCAB) + "-" + random.choice(VOCAB)
    elif r < 0.12:
        w = random.choice(VOCAB) + "'s"
    elif r < 0.16:
        w = str(random.choice([2, 4, 8, 16, 2024, 64]))
    else:
        w = random.choice(VOCAB)
    s = random.random()
    if s < 0.15:
        w = w.upper()
    elif s < 0.35:
        w = w.capitalize()
    return w + random.choice(PUNCT)


with open("corpus.jsonl", "w") as f:
    for i in range(40):
        n = min(110, max(3, int(random.paretovariate(1.3) * 6)))
        text = " ".join(piece() for _ in range(n))
        f.write(json.dumps({"doc_id": f"doc{i:02d}", "text": text}) + "\n")

with open("config.json", "w") as f:
    json.dump({"num_workers": 4}, f)
