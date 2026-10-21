import random
import struct

random.seed(4242)

MAC_A = bytes([2, 0, 0, 0, 0, 1])
MAC_B = bytes([2, 0, 0, 0, 0, 2])


def ipb(s):
    return bytes(int(x) for x in s.split('.'))


def eth(etype, payload, dst=MAC_B):
    return dst + MAC_A + struct.pack('!H', etype) + payload


def ipv4(src, dst, proto, l4):
    hdr = struct.pack('!BBHHHBBH4s4s', 0x45, 0, 20 + len(l4), random.getrandbits(16), 0, 64, proto, 0, ipb(src), ipb(dst))
    return hdr + l4


def tcp(src, dst, sp, dp, fl):
    ack = random.getrandbits(32) if fl & 0x10 else 0
    seg = struct.pack('!HHIIBBHHH', sp, dp, random.getrandbits(32), ack, 0x50, fl, 64240, 0, 0)
    return eth(0x0800, ipv4(src, dst, 6, seg))


def udp(src, dst, sp, dp, n):
    data = bytes(random.getrandbits(8) for _ in range(n))
    seg = struct.pack('!HHHH', sp, dp, 8 + n, 0) + data
    return eth(0x0800, ipv4(src, dst, 17, seg))


def arp(src, dst):
    body = struct.pack('!HHBBH6s4s6s4s', 1, 0x0800, 6, 4, 1, MAC_A, ipb(src), bytes(6), ipb(dst))
    return eth(0x0806, body, dst=bytes([255] * 6))


hosts = ['10.1.0.%d' % i for i in random.sample(range(2, 250), 9)]
scanner, fake, flood, slow, c1, c2, server, target, dns = hosts
frames = []

sp = random.randint(40000, 60000)
for p in random.sample(range(1, 1025), random.randint(45, 55)):
    frames.append(tcp(scanner, target, sp, p, 0x02))

for p in random.sample(range(1024, 9000), random.randint(42, 48)):
    fl = 0x02 if random.random() < 0.15 else random.choice([0x10, 0x18])
    frames.append(tcp(fake, server, random.randint(40000, 60000), p, fl))

for _ in range(random.randint(31, 38)):
    frames.append(tcp(flood, server, random.randint(1024, 65535), random.choice([80, 443]), 0x02))

for p in random.sample(range(1, 1025), random.randint(15, 25)):
    frames.append(tcp(slow, target, random.randint(40000, 60000), p, 0x02))

for c in (c1, c2):
    for _ in range(random.randint(2, 3)):
        csp = random.randint(40000, 60000)
        dp = random.choice([80, 443])
        frames.append(tcp(c, server, csp, dp, 0x02))
        frames.append(tcp(server, c, dp, csp, 0x12))
        frames.append(tcp(c, server, csp, dp, 0x10))
        frames.append(tcp(c, server, csp, dp, 0x18))
        frames.append(tcp(server, c, dp, csp, 0x18))

for _ in range(random.randint(10, 14)):
    frames.append(udp(random.choice([c1, c2, server]), dns, random.randint(40000, 60000), 53, random.randint(10, 30)))

for _ in range(random.randint(6, 10)):
    a, b = random.sample(hosts, 2)
    frames.append(arp(a, b))

random.shuffle(frames)
times = sorted(random.uniform(0, 600) for _ in frames)
base = 1600000000
with open('capture.pcap', 'wb') as f:
    f.write(struct.pack('<IHHiIII', 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
    for t, fr in zip(times, frames):
        sec = int(t)
        usec = int((t - sec) * 1e6)
        f.write(struct.pack('<IIII', base + sec, usec, len(fr), len(fr)))
        f.write(fr)
