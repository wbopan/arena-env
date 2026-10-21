import random
import struct

random.seed(4242)
B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
HEX = "0123456789abcdef"
SERVER = "10.0.0.80"
PATH = "/telemetry/v2/report"


def rb64(n):
    return "".join(random.choice(B64) for _ in range(n))


def rhex(n, alpha=HEX):
    return "".join(random.choice(alpha) for _ in range(n))


def ip2b(s):
    return bytes(int(x) for x in s.split("."))


def csum(b):
    if len(b) % 2:
        b += b"\0"
    s = sum(struct.unpack("!%dH" % (len(b) // 2), b))
    while s >> 16:
        s = (s & 0xFFFF) + (s >> 16)
    return (~s) & 0xFFFF


def frame(src, sport, dst, dport, payload, flags=0x18, opts=False):
    options = b""
    if opts:
        options = b"\x01\x01\x08\x0a" + struct.pack("!II", random.randint(1, 2**31), random.randint(1, 2**31))
    off = (20 + len(options)) // 4
    tcp = struct.pack("!HHIIBBHHH", sport, dport, random.randint(1, 2**31), random.randint(1, 2**31),
                      off << 4, flags, 64240, 0, 0) + options + payload
    total = 20 + len(tcp)
    iph = struct.pack("!BBHHHBBH4s4s", 0x45, 0, total, random.randint(0, 65535), 0x4000, 64, 6, 0,
                      ip2b(src), ip2b(dst))
    iph = iph[:10] + struct.pack("!H", csum(iph)) + iph[12:]
    eth = b"\x02\x00\x00\x00\x00\x02" + b"\x02\x00\x00\x00\x00\x01" + b"\x08\x00"
    return eth + iph + tcp


def fields(blob=None, sig=None, drop=()):
    f = [("dev", "d" + rhex(6)),
         ("blob", blob if blob is not None else rb64(random.randint(82, 100))),
         ("sig", sig if sig is not None else rhex(64))]
    f = [x for x in f if x[0] not in drop]
    random.shuffle(f)
    return f


def request(method="POST", path=PATH, mode_line="X-TLM-Mode: exfil", flds=None, extra_hdr=None):
    body = "&".join(f"{k}={v}" for k, v in flds) if flds is not None else ""
    lines = [f"{method} {path} HTTP/1.1", "Host: tlm.example.com",
             "Content-Type: application/x-www-form-urlencoded"]
    if mode_line:
        lines.append(mode_line)
    if extra_hdr:
        lines.append(extra_hdr)
    lines.append(f"Content-Length: {len(body)}")
    return ("\r\n".join(lines) + "\r\n\r\n" + body).encode()


items = []
modes_pos = ["X-TLM-Mode: exfil", "x-tlm-mode: exfil", "X-TLM-Mode:exfil", "X-Tlm-Mode:   exfil  "]
for i in range(8):
    blob = None
    sig = None
    if i == 0:
        blob = rb64(80)
    if i == 1:
        blob = rb64(88) + "=="
    if i == 2:
        blob = rb64(79) + "="
    if i == 3:
        sig = rhex(64, "0123456789ABCDEF")
    items.append(("req", request(mode_line=random.choice(modes_pos), flds=fields(blob, sig))))

negs = [
    request(method="GET", flds=fields()),
    request(method="PUT", flds=fields()),
    request(path=PATH + "?v=1", flds=fields()),
    request(path=PATH + "/", flds=fields()),
    request(path="/telemetry/v2/reports", flds=fields()),
    request(path="/Telemetry/v2/report", flds=fields()),
    request(mode_line=None, flds=fields()),
    request(mode_line="X-TLM-Mode: normal", flds=fields()),
    request(mode_line="X-TLM-Mode: exfil-test", flds=fields()),
    request(mode_line="X-TLM-Note: exfil", flds=fields()),
    request(mode_line=None, flds=fields() + [("note", "X-TLM-Mode: exfil")]),
    request(flds=fields(blob=rb64(79))),
    request(flds=fields(blob=rb64(45) + "-" + rb64(45))),
    request(flds=fields(blob=rb64(40) + "==" + rb64(45))),
    request(flds=fields(blob=rb64(42) + "%2B" + rb64(42))),
    request(flds=fields(drop=("blob",))),
    request(flds=fields(sig=rhex(63))),
    request(flds=fields(sig=rhex(65))),
    request(flds=fields(sig=rhex(30) + "g" + rhex(33))),
    request(flds=fields(drop=("sig",))),
    request(flds=fields(drop=("blob",)), extra_hdr="X-Debug: blob=" + rb64(90)),
    request(flds=[("xblob", rb64(90)), ("sig", rhex(64))]),
    request(flds=[("blob", rb64(90)), ("sigx", rhex(64))]),
]
for n in negs:
    items.append(("req", n))
for p in ["/status", "/telemetry/v2/report", "/index.html"]:
    items.append(("req", f"GET {p} HTTP/1.1\r\nHost: tlm.example.com\r\n\r\n".encode()))
for _ in range(3):
    body = f"blob={rb64(90)}&sig={rhex(64)}"
    resp = ("HTTP/1.1 200 OK\r\nX-TLM-Mode: exfil\r\nContent-Length: %d\r\n\r\n" % len(body) + body).encode()
    items.append(("resp", resp))
for _ in range(8):
    items.append(("ack", b""))
random.shuffle(items)

records = []
ts = 1710000000
for kind, payload in items:
    client = f"10.1.{random.randint(0, 20)}.{random.randint(2, 250)}"
    cport = random.randint(1024, 65000)
    sport = random.choice([80, 8080])
    opts = random.random() < 0.4
    if kind == "req":
        fr = frame(client, cport, SERVER, sport, payload, 0x18, opts)
    elif kind == "resp":
        fr = frame(SERVER, sport, client, cport, payload, 0x18, opts)
    else:
        fr = frame(client, cport, SERVER, sport, b"", 0x10, opts)
    ts += random.randint(0, 3)
    records.append(struct.pack("<IIII", ts, random.randint(0, 999999), len(fr), len(fr)) + fr)

with open("traffic.pcap", "wb") as f:
    f.write(struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
    for r in records:
        f.write(r)
