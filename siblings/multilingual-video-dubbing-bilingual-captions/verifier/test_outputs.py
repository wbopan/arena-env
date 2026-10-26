from pathlib import Path
import html
import re

ROOT = Path('/root/work')
OUT = ROOT / 'bilingual.vtt'


def read_srt(name):
    result = {}
    text = (ROOT / name).read_text(encoding='utf-8').strip()
    for block in re.split(r'\n\s*\n', text):
        lines = block.splitlines()
        begin, end = lines[1].split(' --> ')
        def ms(stamp):
            h, m, rest = stamp.split(':')
            s, milli = rest.split(',')
            return ((int(h)*60 + int(m))*60 + int(s))*1000 + int(milli)
        result[int(lines[0])] = (ms(begin), ms(end), ' '.join(lines[2:]))
    return result


def expected_cues():
    windows = sorted(read_srt('windows.srt').items(), key=lambda entry: entry[1][0])
    en, translated = read_srt('source_text.srt'), read_srt('target_text.srt')
    lang = (ROOT / 'target_language.txt').read_text().strip().upper()
    answer = []
    for pos, (identifier, (start, end, _)) in enumerate(windows):
        prior_end = windows[pos-1][1][1] if pos else 0
        next_start = windows[pos+1][1][0] if pos+1 < len(windows) else end+80
        answer.append((f'seg-{identifier}', max(0, start-80, prior_end), min(end+80, next_start),
                       'EN: ' + html.escape(en[identifier][2], quote=False),
                       lang + ': ' + html.escape(translated[identifier][2], quote=False)))
    return answer


def actual_cues():
    blocks = OUT.read_text(encoding='utf-8').split('\n\n')
    assert blocks[0] == 'WEBVTT'
    assert blocks[-1] == ''
    result = []
    for block in blocks[1:-1]:
        lines = block.split('\n')
        assert len(lines) == 4
        a, b = lines[1].split(' --> ')
        def ms(t):
            match = re.fullmatch(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})', t)
            assert match
            h, m, s, milli = map(int, match.groups())
            return ((h*60+m)*60+s)*1000+milli
        result.append((lines[0], ms(a), ms(b), lines[2], lines[3]))
    return result


def test_exists():
    assert OUT.is_file()


def test_webvtt_structure():
    assert OUT.read_text(encoding='utf-8').startswith('WEBVTT\n\n')
    assert len(actual_cues()) == len(expected_cues())


def test_ids_and_order():
    assert [c[0] for c in actual_cues()] == [c[0] for c in expected_cues()]


def test_extended_times():
    assert [c[1:3] for c in actual_cues()] == [c[1:3] for c in expected_cues()]


def test_bilingual_escaped_text():
    assert [c[3:] for c in actual_cues()] == [c[3:] for c in expected_cues()]
