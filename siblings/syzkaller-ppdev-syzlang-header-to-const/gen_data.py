import random

random.seed(20240611)

TYPES = ["char", "unsigned char", "short", "unsigned short", "int",
         "unsigned int", "long", "unsigned long", "long long"]

tc = random.choice("abcdeghjkmnqrstuvwxyz")
lines = ["/* zq.h - userspace API for the zq parallel port device */",
         "#ifndef _UAPI_ZQ_H", "#define _UAPI_ZQ_H", "",
         f"#define ZQ_IOCTL '{tc}'  /* ioctl type */", ""]

struct_names = ["zq_frob_struct", "zq_timing", "zq_buf_desc"]
for sname in struct_names:
    n = random.randint(2, 5)
    lines.append(f"struct {sname} {{")
    for i in range(n):
        t = random.choice(TYPES)
        cm = "  /* field */" if random.random() < 0.3 else ""
        lines.append(f"\t{t} f{i};{cm}")
    lines.append("};")
    lines.append("")

words = ["CLAIM", "RELEASE", "YIELD", "EXCL", "SETMODE", "GETMODE", "RSTATUS",
         "WDATA", "RDATA", "WCONTROL", "RCONTROL", "FCONTROL", "DATADIR", "NEGOT",
         "SETPHASE", "GETPHASE", "SETTIME", "GETTIME", "GETMODES", "SETFLAGS",
         "GETFLAGS", "WCTLONIRQ", "CLRIRQ"]
chosen = random.sample(words, 16)
nrs = random.sample(range(0x80, 0xC0), 16)
for name, nr in zip(chosen, nrs):
    kind = random.choice(["_IO", "_IOR", "_IOW", "_IOWR"])
    tt = "ZQ_IOCTL" if random.random() < 0.75 else f"'{tc}'"
    if kind == "_IO":
        val = f"_IO({tt}, 0x{nr:x})"
    else:
        if random.random() < 0.4:
            arg = "struct " + random.choice(struct_names)
        else:
            arg = random.choice(TYPES)
        val = f"{kind}({tt}, 0x{nr:x}, {arg})"
    cm = "\t/* cmd */" if random.random() < 0.3 else ""
    lines.append(f"#define ZQ{name} {val}{cm}")
lines.append("")

flag_names = ["ZQ_MODE_COMPAT", "ZQ_MODE_NIBBLE", "ZQ_MODE_BYTE", "ZQ_MODE_EPP",
              "ZQ_MODE_ECP", "ZQ_MODE_ECPRLE", "ZQ_FLAG_FASTWRITE", "ZQ_FLAG_FASTREAD",
              "ZQ_FLAG_RLE", "ZQ_FLAG_SWE", "ZQ_FLAG_ADDR", "ZQ_FLAG_IRQ"]
for fname in random.sample(flag_names, 10):
    form = random.choice(["hex", "dec", "shift"])
    if form == "hex":
        val = f"0x{random.randint(1, 0xffff):x}"
    elif form == "dec":
        val = str(random.randint(1, 5000))
    else:
        val = f"(1 << {random.randint(0, 20)})"
    cm = " /* flag */" if random.random() < 0.3 else ""
    lines.append(f"#define {fname} {val}{cm}")
lines.append("")
lines.append("#endif /* _UAPI_ZQ_H */")

with open("zq.h", "w") as f:
    f.write("\n".join(lines) + "\n")
