from pathlib import Path
import json
import random

random.seed(74021)
magic = bytes([random.randint(35, 120), random.randint(35, 120)])
remainder = random.randrange(11)
data = bytearray(magic)
for i in range(8):
    data.append(0 if i == 3 else random.randint(12, 240))
data.append((remainder - sum(data)) % 11)
Path('crash.bin').write_bytes(data)
Path('crash_rule.json').write_text(json.dumps({'magic_hex': magic.hex(), 'remainder': remainder}), encoding='utf-8')
