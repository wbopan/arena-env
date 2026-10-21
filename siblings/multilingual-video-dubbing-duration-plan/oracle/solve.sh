#!/bin/bash
set -e
cd /root/work
cat > /tmp/plan.py << 'EOF'
import csv, json

def sec(t):
    a, ms = t.strip().split(',')
    h, m, s = a.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

def srt(p):
    out = {}
    for b in open(p, encoding='utf-8').read().replace('\r\n', '\n').strip().split('\n\n'):
        ls = b.strip().split('\n')
        x, y = ls[1].split('-->')
        out[int(ls[0])] = (sec(x), sec(y), ' '.join(l.strip() for l in ls[2:]).strip())
    return out

win = srt('segments.srt')
txt = srt('target_text.srt')
tts = {int(r['segment_index']): float(r['tts_duration_sec']) for r in csv.DictReader(open('tts_durations.csv'))}
lang = open('target_language.txt').read().strip()
segs = []
summ = {'pad_silence': 0, 'rate_adjust': 0, 'trim': 0}
tot = 0.0
for i in sorted(win, key=lambda k: win[k][0]):
    s, e, _ = win[i]
    w = e - s
    d = tts[i]
    r = d / w
    if r <= 1:
        c, tf, tr, se = 'pad_silence', 1.0, 0.0, s + d
    elif r <= 1.25:
        c, tf, tr, se = 'rate_adjust', r, 0.0, e
    else:
        c, tf, tr, se = 'trim', 1.25, d / 1.25 - w, e
    summ[c] += 1
    tot += tr
    segs.append({'index': i, 'window_start_sec': round(s, 3), 'window_end_sec': round(e, 3),
                 'window_duration_sec': round(w, 3), 'tts_duration_sec': round(d, 3),
                 'duration_control': c, 'tempo_factor': round(tf, 3), 'trimmed_sec': round(tr, 3),
                 'speech_end_sec': round(se, 3), 'target_text': txt[i][2]})
summ['total_trimmed_sec'] = round(tot, 3)
json.dump({'target_language': lang, 'segments': segs, 'summary': summ},
          open('dub_plan.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
EOF
python3 /tmp/plan.py
