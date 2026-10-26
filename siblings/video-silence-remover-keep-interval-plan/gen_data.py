import json
import random

random.seed(80231)
duration = random.randint(69, 85)
opening_end = random.randint(7, 12)
first = [{'start': -3, 'end': opening_end},
         {'start': 23, 'end': 29},
         {'start': 47, 'end': 51}]
second = [{'start': opening_end, 'end': opening_end + 2},
          {'start': 26, 'end': 33},
          {'start': 36, 'end': 36 + random.randint(3, 7)},
          {'start': 49, 'end': 54},
          {'start': duration - 4, 'end': duration + 5}]
random.shuffle(first)
random.shuffle(second)
for name, obj in [('recording.json', {'duration_seconds': duration}),
                  ('opening.json', {'segments': first}),
                  ('pauses.json', {'segments': second})]:
    with open(name, 'w') as f:
        json.dump(obj, f, indent=2)
