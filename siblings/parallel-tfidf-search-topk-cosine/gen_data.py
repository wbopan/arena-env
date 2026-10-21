import json
import random

random.seed(20240611)

VOCAB = ["index", "search", "query", "vector", "matrix", "worker", "thread", "process",
         "memory", "cache", "shard", "token", "corpus", "score", "rank", "cosine",
         "weight", "term", "document", "engine", "parallel", "chunk", "queue", "merge",
         "reduce", "latency", "speedup", "core", "pool", "python", "numpy", "sparse",
         "dense", "hash", "sort", "heap", "graph", "node", "batch", "stream", "buffer",
         "lock", "signal", "kernel", "schedule", "balance", "split", "join", "filter", "v2"]
PUNCT = ["", "", "", ",", ".", ";", "!", "?"]


def word(w):
    r = random.random()
    if r < 0.15:
        w = w.upper()
    elif r < 0.35:
        w = w.capitalize()
    return w + random.choice(PUNCT)


with open("corpus.jsonl", "w") as f:
    for i in range(60):
        fav = random.sample(VOCAB, 6)
        n = random.randint(15, 38)
        toks = []
        for _ in range(n):
            w = random.choice(fav) if random.random() < 0.6 else random.choice(VOCAB)
            toks.append(word(w))
        f.write(json.dumps({"doc_id": f"d{i:03d}", "text": " ".join(toks)}) + "\n")

queries = []
for q in range(9):
    k = random.randint(2, 4)
    ws = random.sample(VOCAB, k)
    if q == 3:
        ws.append(ws[0])
    if q == 5:
        ws.append("zeppelin")
    queries.append({"qid": f"q{q + 1:02d}", "text": " ".join(word(w) for w in ws)})
queries.append({"qid": "q10", "text": "Zeppelin quasar, xylophone!"})

with open("queries.json", "w") as f:
    json.dump(queries, f, indent=1)
