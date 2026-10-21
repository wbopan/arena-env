import json
import re
import struct
from pathlib import Path

import pytest

WORK = Path("/root/work")
PCAP = WORK / "traffic.pcap"
OUT = WORK / "alerts.json"
TARGET = "/telemetry/v2/report"
B64RE = re.compile(r"[A-Za-z0-9+/]+={0,2}")
HEXRE = re.compile(r"[0-9a-fA-F]{64}")


def _records():
    data = PCAP.read_bytes()
    magic = struct.unpack("<I", data[:4])[0]
    e = "<" if magic == 0xA1B2C3D4 else ">"
    pos = 24
    idx = 0
    while pos + 16 <= len(data):
        incl = struct.unpack(e + "IIII", data[pos:pos + 16])[2]
        pos += 16
        fr = data[pos:pos + incl]
        pos += incl
        idx += 1
        yield idx, fr


def _is_exfil(pl):
    sep = pl.find(b"\r\n\r\n")
    if sep < 0:
        return False
    head = pl[:sep].decode("latin-1").split("\r\n")
    body = pl[sep + 4:].decode("latin-1")
    parts = head[0].split(" ")
    if len(parts) != 3 or parts[0] != "POST" or parts[1] != TARGET:
        return False
    ok = False
    for h in head[1:]:
        if ":" in h:
            n, v = h.split(":", 1)
            if n.strip().lower() == "x-tlm-mode" and v.strip() == "exfil":
                ok = True
    if not ok:
        return False
    kv = {}
    for p in body.split("&"):
        if "=" in p:
            k, v = p.split("=", 1)
            kv.setdefault(k, v)
    b = kv.get("blob")
    s = kv.get("sig")
    if b is None or s is None:
        return False
    return len(b) >= 80 and B64RE.fullmatch(b) is not None and HEXRE.fullmatch(s) is not None


def _expected():
    res = []
    for idx, fr in _records():
        if len(fr) < 34 or fr[12:14] != b"\x08\x00":
            continue
        ip = fr[14:]
        if ip[9] != 6:
            continue
        ihl = (ip[0] & 15) * 4
        tot = struct.unpack("!H", ip[2:4])[0]
        tcp = ip[ihl:tot]
        off = (tcp[12] >> 4) * 4
        pl = tcp[off:]
        if _is_exfil(pl):
            src = ".".join(str(x) for x in ip[12:16]) + ":" + str(struct.unpack("!H", tcp[0:2])[0])
            res.append({"packet": idx, "src": src})
    return res


def _load():
    assert OUT.exists(), "alerts.json missing"
    return json.loads(OUT.read_text())


def test_output_exists_and_valid_json():
    d = _load()
    assert isinstance(d, dict)


def test_schema():
    d = _load()
    assert isinstance(d.get("count"), int)
    assert isinstance(d.get("alerts"), list)
    for a in d["alerts"]:
        assert isinstance(a, dict)
        assert isinstance(a.get("packet"), int)
        assert isinstance(a.get("src"), str)


def test_count():
    d = _load()
    exp = _expected()
    assert d["count"] == len(exp)
    assert len(d["alerts"]) == len(exp)


def test_packet_indices():
    d = _load()
    exp = _expected()
    assert sorted(a["packet"] for a in d["alerts"]) == [e["packet"] for e in exp]


def test_src_and_order():
    d = _load()
    exp = _expected()
    got = [{"packet": a["packet"], "src": a["src"]} for a in d["alerts"]]
    assert got == exp
