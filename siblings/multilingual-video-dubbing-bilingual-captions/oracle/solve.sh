#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_bilingual.py <<'PY'
from pathlib import Path
import html
import re

root = Path('/root/work')
def parse(name):
    items = {}
    for block in re.split(r'\n\s*\n', (root/name).read_text(encoding='utf-8').strip()):
        rows = block.splitlines()
        a, b = rows[1].split(' --> ')
        def millis(t):
            h, m, tail = t.split(':')
            s, frac = tail.split(',')
            return 3600000*int(h) + 60000*int(m) + 1000*int(s) + int(frac)
        items[int(rows[0])] = (millis(a), millis(b), ' '.join(rows[2:]))
    return items

def vtt_time(ms):
    h, remain = divmod(ms, 3600000)
    m, remain = divmod(remain, 60000)
    s, frac = divmod(remain, 1000)
    return f'{h:02d}:{m:02d}:{s:02d}.{frac:03d}'
windows = sorted(parse('windows.srt').items(), key=lambda item: item[1][0])
source, target = parse('source_text.srt'), parse('target_text.srt')
lang = (root/'target_language.txt').read_text().strip().upper()
parts = ['WEBVTT\n\n']
for j, (key, (start, end, _)) in enumerate(windows):
    lower = windows[j-1][1][1] if j else 0
    upper = windows[j+1][1][0] if j+1 < len(windows) else end+80
    a, b = max(0, start-80, lower), min(end+80, upper)
    parts.append(f'seg-{key}\n{vtt_time(a)} --> {vtt_time(b)}\nEN: {html.escape(source[key][2], quote=False)}\n{lang}: {html.escape(target[key][2], quote=False)}\n\n')
(root/'bilingual.vtt').write_text(''.join(parts), encoding='utf-8')
PY
python /tmp/solve_bilingual.py
