#!/usr/bin/env bash
set -euo pipefail
cat > /root/work/solve_energy.py <<'PY'
import json
import math
import struct
import wave
from pathlib import Path

root = Path('/root/work')
with wave.open(str(root / 'lecture_audio.wav'), 'rb') as f:
    rate = f.getframerate()
    raw = f.readframes(f.getnframes())
samples = struct.unpack('<' + 'h' * (len(raw) // 2), raw)
width = rate // 2
energies = []
for i in range(0, len(samples), width):
    part = samples[i:i + width]
    energies.append(math.sqrt(sum(float(v) ** 2 for v in part) / len(part)))
avg = sum(energies) / len(energies)
stats = {'min': min(energies), 'max': max(energies), 'mean': avg,
         'std': math.sqrt(sum((v - avg) ** 2 for v in energies) / len(energies))}
result = {'sample_rate': rate, 'window_seconds': 0.5,
          'total_seconds': len(energies) * 0.5,
          'energies': [round(v, 3) for v in energies],
          'stats': {key: round(value, 3) for key, value in stats.items()}}
(root / 'energies.json').write_text(json.dumps(result, indent=2) + '\n')
PY
python3 /root/work/solve_energy.py
