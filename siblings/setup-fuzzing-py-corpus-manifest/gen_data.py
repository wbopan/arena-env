from pathlib import Path
import json
import random

random.seed(48116)
folder = Path('seeds')
folder.mkdir(exist_ok=True)
values = [{'id': random.randint(10, 999), 'enabled': True}, [random.randint(1, 20), {'kind': 'packet'}], {'name': 'é', 'ports': [80, 443]}]
for i, value in enumerate(values):
    folder.joinpath(f'json_{i}_compact.seed').write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')), encoding='utf-8')
    folder.joinpath(f'json_{i}_spaced.seed').write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
for i in range(4):
    word = random.choice(['HEAD', 'proto', 'ERR', 'field'])
    folder.joinpath(f'text_{i}.seed').write_text(word + ':' + str(random.randint(100, 999)) + '\n', encoding='utf-8')
folder.joinpath('text_repeat.seed').write_bytes(folder.joinpath('text_0.seed').read_bytes())
for i in range(4):
    folder.joinpath(f'binary_{i}.seed').write_bytes(bytes([255, random.randrange(20, 250), 0, i]) + random.randbytes(i))
folder.joinpath('binary_repeat.seed').write_bytes(folder.joinpath('binary_0.seed').read_bytes())
