import ipaddress
import random
import struct

random.seed(62508)


def address(ip):
    return ipaddress.IPv4Address(ip).packed


def frame(proto, src, dst, sport, dport, payload_size):
    body = bytes(random.getrandbits(8) for _ in range(payload_size))
    if proto == 'TCP':
        transport = struct.pack('!HHIIHHHH', sport, dport, 0, 0, 0x5002, 4096, 0, 0) + body
        protocol = 6
    else:
        transport = struct.pack('!HHHH', sport, dport, 8 + len(body), 0) + body
        protocol = 17
    ip = struct.pack('!BBHHHBBH4s4s', 0x45, 0, 20 + len(transport), 0, 0, 64,
                     protocol, 0, address(src), address(dst))
    return b'\xaa\xbb\xcc\xdd\xee\xff' + b'\x11\x22\x33\x44\x55\x66' + b'\x08\x00' + ip + transport


flows = [
    ('TCP', '10.7.0.1', '10.7.0.2', 40001, 443),
    ('TCP', '10.7.0.2', '10.7.0.1', 443, 40001),
    ('TCP', '10.7.0.1', '10.7.0.3', 40002, 22),
    ('TCP', '10.7.0.4', '10.7.0.3', 51515, 80),
    ('TCP', '10.7.0.3', '10.7.0.4', 80, 51515),
    ('UDP', '10.7.0.1', '10.7.0.4', 53000, 53),
    ('UDP', '10.7.0.4', '10.7.0.1', 53, 53000),
    ('UDP', '10.7.0.2', '10.7.0.3', 60001, 123),
    ('UDP', '10.7.0.2', '10.7.0.3', 60002, 123),
]
packets = []
for flow in flows:
    for _ in range(random.randint(2, 8)):
        packets.append(frame(*flow, random.randint(0, 45)))
for _ in range(4):
    packets.append(b'\xff' * 12 + b'\x08\x06' + bytes(random.getrandbits(8) for _ in range(28)))
random.shuffle(packets)
with open('capture.pcap', 'wb') as f:
    f.write(struct.pack('<IHHIIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1))
    for i, packet in enumerate(packets):
        f.write(struct.pack('<IIII', 1700000000 + i // 10, (i % 10) * 100000, len(packet), len(packet)))
        f.write(packet)
