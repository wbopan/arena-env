import json
import random

random.seed(4242)

GROUPS = ['com.google.auto', 'com.google.guava', 'org.ow2.asm', 'com.squareup',
          'org.checkerframework', 'com.google.errorprone', 'io.grpc', 'com.google.protobuf',
          'net.bytebuddy', 'org.slf4j']
WORDS = ['common', 'core', 'api', 'util', 'annotations', 'runtime', 'compiler', 'service',
         'value', 'factory', 'processor', 'testing']
SFX = ['', '-lite', '-jdk8', '-shaded']
names = random.sample([w + s for w in WORDS for s in SFX], 26)
arts = [random.choice(GROUPS) + ':' + n for n in names]

versions = {}
for a in arts:
    k = random.randint(1, 3)
    vs = set()
    while len(vs) < k:
        vs.add('%d.%d.%d' % (random.randint(1, 4), random.randint(0, 12), random.randint(0, 5)))
    versions[a] = sorted(vs)

repo = {}
for i, a in enumerate(arts):
    later = arts[i + 1:]
    for v in versions[a]:
        deps = []
        if later:
            for b in random.sample(later, min(len(later), random.randint(0, 3))):
                deps.append({'coord': b + ':' + random.choice(versions[b]),
                             'optional': random.random() < 0.15})
        repo[a + ':' + v] = deps

with open('repository.json', 'w') as f:
    json.dump(repo, f, indent=1, sort_keys=True)

direct = random.sample(arts[:10], 5)
L = ['<?xml version="1.0" encoding="UTF-8"?>',
     '<project xmlns="http://maven.apache.org/POM/4.0.0">',
     '  <modelVersion>4.0.0</modelVersion>',
     '  <groupId>com.example</groupId>',
     '  <artifactId>app</artifactId>',
     '  <version>1.0.0</version>',
     '  <dependencies>']
for a in direct:
    g, n = a.split(':')
    L += ['    <dependency>', '      <groupId>' + g + '</groupId>',
          '      <artifactId>' + n + '</artifactId>',
          '      <version>' + random.choice(versions[a]) + '</version>']
    if random.random() < 0.2:
        L.append('      <optional>true</optional>')
    L.append('    </dependency>')
L += ['  </dependencies>', '</project>']
with open('pom.xml', 'w') as f:
    f.write('\n'.join(L) + '\n')
