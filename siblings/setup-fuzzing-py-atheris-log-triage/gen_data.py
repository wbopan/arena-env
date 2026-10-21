import os
import random

random.seed(1337)

LIBS = ["ujson_lite", "yamlish", "csvkit_mini", "tomlparse", "msgpack_py", "urlnorm"]
CRASH = {
    "yamlish": ("RecursionError", "maximum recursion depth exceeded while calling a Python object"),
    "tomlparse": ("json.decoder.JSONDecodeError", "Expecting value: line 1 column 1 (char 0)"),
    "urlnorm": ("KeyError", "'scheme: missing'"),
}
MUTS = ["ChangeByte-", "InsertByte-", "CrossOver-", "EraseBytes-", "CopyPart-", "ShuffleBytes-", "ChangeBit-"]

os.makedirs("logs", exist_ok=True)


def status(n, ev, cov, ft, cu, cb, extra=""):
    es = 0 if n < 10 else random.randint(200, 9000)
    rss = random.randint(36, 60)
    return f"#{n}\t{ev}  cov: {cov} ft: {ft} corp: {cu}/{cb}b lim: 4096 exec/s: {es} rss: {rss}Mb{extra}"


for lib in LIBS:
    lines = []
    pid = random.randint(100, 9999)
    lines.append(f"INFO: Using built-in libfuzzer")
    lines.append(f"WARNING: Failed to find function \"__sanitizer_acquire_crash_state\".")
    lines.append(f"INFO: Running with entropic power schedule (0xFF, 100).")
    lines.append(f"INFO: Seed: {random.randint(10**8, 10**9)}")
    lines.append(f"INFO: -max_len is not provided; libFuzzer will not generate inputs larger than 4096 bytes")
    lines.append(f"INFO: A corpus is not provided, starting from an empty corpus")
    n = 2
    cov = random.randint(5, 30)
    ft = cov + random.randint(0, 5)
    cu, cb = 1, 1
    lines.append(status(n, "INITED", cov, ft, cu, cb))
    for _ in range(random.randint(25, 55)):
        ev = random.choices(["NEW", "REDUCE", "pulse"], [5, 2, 1])[0]
        if ev == "pulse":
            n = 1 << n.bit_length()
            lines.append(status(n, "pulse", cov, ft, cu, cb))
            continue
        n += random.randint(1, 400)
        if ev == "NEW":
            cov += random.randint(0, 3)
            ft += random.randint(1, 4)
            cu += 1
            cb += random.randint(1, 12)
        else:
            ft += random.randint(0, 1)
            cb = max(cu, cb - random.randint(1, 5))
        k = random.randint(1, 4)
        ms = "".join(random.choice(MUTS) for _ in range(k))
        L = random.randint(1, 40)
        extra = f" L: {L}/{L + random.randint(0, 20)} MS: {k} {ms}"
        lines.append(status(n, ev, cov, ft, cu, cb, extra))
    if lib in CRASH:
        et, msg = CRASH[lib]
        lines.append("")
        lines.append(" === Uncaught Python exception: ===".strip())
        lines.append(f"{et}: {msg}")
        lines.append("Traceback (most recent call last):")
        lines.append(f"  File \"/app/{lib}/fuzz.py\", line {random.randint(10, 30)}, in TestOneInput")
        lines.append(f"    {lib}.loads(data)")
        lines.append(f"  File \"/app/{lib}/{lib}/core.py\", line {random.randint(40, 300)}, in loads")
        lines.append("    # cov: 999 ft: 999 corp: 99/99b")
        lines.append("")
        lines.append(f"=={pid}== ERROR: libFuzzer: fuzz target exited")
        lines.append(f"MS: 2 ChangeByte-CrossOver-; base unit: {random.getrandbits(160):040x}")
        lines.append("0x5b,0x5b,")
        lines.append("[[")
        lines.append(f"artifact_prefix='./'; Test unit written to ./crash-{random.getrandbits(160):040x}")
        lines.append("Base64: W1s=")
    else:
        n += random.randint(1, 5000)
        lines.append(status(n, "DONE", cov, ft, cu, cb))
        lines.append(f"Done {n} runs in 11 second(s)")
    with open(os.path.join("logs", f"{lib}.log"), "w") as f:
        f.write("\n".join(lines) + "\n")
