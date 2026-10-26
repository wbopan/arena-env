import random
from pathlib import Path

random.seed(9203)
ids = random.sample(range(10, 90), 4)
starts = [220 + random.randrange(0, 25), 910 + random.randrange(0, 25), 1640 + random.randrange(0, 25), 2300 + random.randrange(0, 25)]
ends = [a + length for a, length in zip(starts, [310, 370, 295, 340])]
source = ['Ready & waiting', 'Check <camera>', 'We move now', 'That is > enough']
target = ['Listos & atentos', 'Mira <camara>', 'Vamos ahora', 'Eso es > suficiente']
def stamp(ms):
    return f'00:00:{ms//1000:02d},{ms%1000:03d}'
def write_srt(name, rows):
    Path(name).write_text(''.join(f'{i}\n{stamp(a)} --> {stamp(b)}\n{text}\n\n' for i, a, b, text in rows), encoding='utf-8')
write_srt('windows.srt', [(i, a, b, 'window') for i, a, b in zip(ids, starts, ends)])
order = list(range(4))
random.shuffle(order)
write_srt('source_text.srt', [(ids[j], 0, 100, source[j]) for j in order])
random.shuffle(order)
write_srt('target_text.srt', [(ids[j], 50, 150, target[j]) for j in order])
Path('target_language.txt').write_text('es\n', encoding='utf-8')
