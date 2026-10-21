import random

random.seed(731)

WORDS = ["load", "parse", "token", "batch", "merge", "split", "score", "index",
         "cache", "record", "stream", "window", "filter", "encode", "decode",
         "header", "schema", "field", "value", "count", "normalize", "resolve",
         "build", "fetch", "route", "shard", "limit", "flush", "meta", "v2"]
PRIMS = ["int", "float", "str", "bool", "bytes"]


def simple():
    r = random.random()
    if r < 0.6:
        return random.choice(PRIMS)
    if r < 0.8:
        return f"list[{random.choice(PRIMS)}]"
    return f"dict[str, {random.choice(PRIMS)}]"


def gen_type(d=0):
    if d >= 2 or random.random() < 0.4:
        return random.choice(PRIMS)
    k = random.choice(["list", "dict", "set", "tuple", "opt", "union"])
    if k == "list":
        return f"list[{gen_type(d + 1)}]"
    if k == "set":
        return f"set[{random.choice(['int', 'str'])}]"
    if k == "dict":
        return f"dict[{random.choice(['str', 'int'])}, {gen_type(d + 1)}]"
    if k == "tuple":
        n = random.randint(2, 3)
        return "tuple[" + ", ".join(gen_type(d + 1) for _ in range(n)) + "]"
    if k == "opt":
        return f"Optional[{simple()}]"
    return f"{simple()} | None"


def snake(n):
    return "_".join(random.sample(WORDS, n))


lines = ["# Service API surface (type stubs)", "from typing import Optional", "", ""]
used = set()
funcs = []
while len(funcs) < 22:
    base = snake(random.randint(2, 3))
    if base in used:
        continue
    used.add(base)
    private = random.random() < 0.25 or len(funcs) == 2
    name = ("_" + base) if private else base
    nparams = random.randint(0, 3)
    pnames = []
    while len(pnames) < nparams:
        p = snake(random.randint(1, 2))
        if p not in pnames:
            pnames.append(p)
    params = ", ".join(f"{p}: {gen_type()}" for p in pnames)
    ret = "None" if random.random() < 0.15 else gen_type()
    funcs.append(f"def {name}({params}) -> {ret}:\n    ...\n\n")

cls = ("class Registry:\n"
       "    def register_item(self, item_id: int, tags: list[str]) -> bool:\n"
       "        ...\n\n"
       "    def _drop_item(self, item_id: int) -> None:\n"
       "        ...\n\n\n")

body = "".join(funcs[:11]) + cls + "".join(funcs[11:])
with open("api.py", "w") as f:
    f.write("\n".join(lines) + body)
