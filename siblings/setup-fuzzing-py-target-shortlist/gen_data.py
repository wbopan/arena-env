from pathlib import Path
import random

random.seed(20250317)
Path('pkg').mkdir(exist_ok=True)
Path('tests').mkdir(exist_ok=True)
Path('pkg/__init__.py').write_text('', encoding='utf-8')
names = ['parse_packet', 'decode_frame', 'load_record', 'validate_key', 'normalize_text', 'format_label', 'parse_token', 'decode_hint']
random.shuffle(names)
for module, chunk in [('wire', names[:4]), ('records', names[4:])]:
    lines = []
    for i, name in enumerate(chunk):
        arg = random.choice(['data', 'payload', 'text', 'raw', 'value', 'item'])
        lines.append(f'def {name}({arg}):\n    return str({arg}).strip()[:{i + 2}]\n')
    lines.append('def _internal(data):\n    return data\n')
    Path(f'pkg/{module}.py').write_text('\n'.join(lines), encoding='utf-8')
    for i, name in enumerate(chunk):
        count = random.randint(0, 2)
        for j in range(count):
            Path(f'tests/test_{module}_{i}_{j}.py').write_text(
                f'from pkg.{module} import {name}\n\ndef test_case():\n    assert isinstance({name}("abc"), str)\n    {name}("xyz")\n', encoding='utf-8')
