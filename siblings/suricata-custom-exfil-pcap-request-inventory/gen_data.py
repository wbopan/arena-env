import ipaddress
import random
import struct

random.seed(6621)
frames = []

def packet(src, dst, sport, dport, seq, flags, payload=b''):
    eth = bytes.fromhex('0200000000020200000000010800')
    srcb, dstb = ipaddress.IPv4Address(src).packed, ipaddress.IPv4Address(dst).packed
    total = 20 + 20 + len(payload)
    ip = struct.pack('!BBHHHBBH4s4s', 69, 0, total, 0, 0, 64, 6, 0, srcb, dstb)
    tcp = struct.pack('!HHIIBBHHH', sport, dport, seq, 0, 80, flags, 4096, 0, 0)
    return eth + ip + tcp + payload

for i in range(8):
    src = f'10.4.0.{i + 2}'
    port = 31000 + i * 13
    initial = 70000 + i * 1000
    method = 'GET' if i % 3 == 0 else 'POST'
    uri = '/telemetry/v2/report' if i % 2 else '/status'
    body = b'' if method == 'GET' else bytes(random.randrange(32, 127) for _ in range(18 + i * 9))
    request = (f'{method} {uri} HTTP/1.1\r\nHost: collector.test\r\n'
               f'Content-Length: {len(body)}\r\n\r\n').encode() + body
    a, b = 17, len(request) // 2
    pieces = [(0, request[:a]), (a, request[a:b]), (b, request[b:])]
    frames.append(packet(src, '10.4.1.1', port, 80, initial, 2))
    for offset, data in (pieces[1], pieces[0], pieces[2]):
        frames.append(packet(src, '10.4.1.1', port, 80, initial + 1 + offset, 24, data))
    frames.append(packet('10.4.1.1', src, 80, port, 9000 + i, 16))

with open('telemetry.pcap', 'wb') as f:
    f.write(struct.pack('<IHHIIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1))
    for j, frame in enumerate(frames):
        f.write(struct.pack('<IIII', 1700000000 + j, 0, len(frame), len(frame)))
        f.write(frame)
