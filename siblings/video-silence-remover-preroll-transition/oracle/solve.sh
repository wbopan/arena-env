#!/usr/bin/env bash
set -euo pipefail
cat > /root/work/solve_preroll.py <<'PY'
import json
from pathlib import Path

root = Path('/root/work')
energy = json.loads((root / 'energies.json').read_text())['energies']
threshold = 2 * sum(energy[:6]) / 6
smooth = []
for i in range(len(energy)):
    portion = energy[max(0, i - 2):i + 1]
    smooth.append(sum(portion) / len(portion))
end = 0
for i in range(6, len(energy) - 2):
    if all(smooth[j] > threshold for j in (i, i + 1, i + 2)):
        end = i
        break
segments = [{'start': 0, 'end': end, 'duration': end}] if end else []
result = {'method': 'trailing_energy_transition', 'threshold': round(threshold, 3),
          'segments': segments, 'total_segments': len(segments),
          'total_duration_seconds': end}
(root / 'initial_silence.json').write_text(json.dumps(result, indent=2) + '\n')
PY
python3 /root/work/solve_preroll.py
