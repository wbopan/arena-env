import json
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'keep_plan.json'


def expected():
    duration = json.loads((ROOT / 'recording.json').read_text())['duration_seconds']
    removed = [False] * duration
    for filename in ('opening.json', 'pauses.json'):
        for segment in json.loads((ROOT / filename).read_text())['segments']:
            for second in range(max(0, segment['start']), min(duration, segment['end'])):
                removed[second] = True
    keep = []
    start = None
    for second in range(duration + 1):
        retained = second < duration and not removed[second]
        if retained and start is None:
            start = second
        elif not retained and start is not None:
            keep.append({'start': start, 'end': second, 'duration': second - start})
            start = None
    return duration, sum(removed), keep


def test_file_exists():
    assert OUT.is_file()


def test_schema():
    obj = json.loads(OUT.read_text())
    assert set(obj) == {'original_duration_seconds', 'removed_duration_seconds',
                        'output_duration_seconds', 'keep_segments'}
    assert isinstance(obj['keep_segments'], list)
    assert all(set(s) == {'start', 'end', 'duration'} for s in obj['keep_segments'])
    assert all(type(s[k]) is int for s in obj['keep_segments'] for k in s)


def test_keep_intervals():
    _, _, keep = expected()
    assert json.loads(OUT.read_text())['keep_segments'] == keep


def test_duration_totals():
    duration, removed, keep = expected()
    obj = json.loads(OUT.read_text())
    assert obj['original_duration_seconds'] == duration
    assert obj['removed_duration_seconds'] == removed
    assert obj['output_duration_seconds'] == sum(s['duration'] for s in keep)
    assert obj['original_duration_seconds'] == obj['removed_duration_seconds'] + obj['output_duration_seconds']
