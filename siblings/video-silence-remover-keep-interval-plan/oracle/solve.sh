#!/usr/bin/env bash
set -euo pipefail
cat > /root/work/solve_keep.py <<'PY'
import json
from pathlib import Path

root = Path('/root/work')
duration = json.loads((root / 'recording.json').read_text())['duration_seconds']
intervals = []
for filename in ('opening.json', 'pauses.json'):
    for segment in json.loads((root / filename).read_text())['segments']:
        left = max(0, segment['start'])
        right = min(duration, segment['end'])
        if left < right:
            intervals.append((left, right))
intervals.sort()
merged = []
for left, right in intervals:
    if merged and left <= merged[-1][1]:
        merged[-1][1] = max(merged[-1][1], right)
    else:
        merged.append([left, right])
keep = []
cursor = 0
for left, right in merged + [[duration, duration]]:
    if cursor < left:
        keep.append({'start': cursor, 'end': left, 'duration': left - cursor})
    cursor = right
removed = sum(right - left for left, right in merged)
result = {'original_duration_seconds': duration,
          'removed_duration_seconds': removed,
          'output_duration_seconds': duration - removed,
          'keep_segments': keep}
(root / 'keep_plan.json').write_text(json.dumps(result, indent=2) + '\n')
PY
python3 /root/work/solve_keep.py
