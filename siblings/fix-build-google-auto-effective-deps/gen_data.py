import os
import random

random.seed(20240611)


def ver():
    return '%d.%d.%d' % (random.randint(1, 9), random.randint(0, 20), random.randint(0, 9))


PARENT_VER = '1.4.0'
props = {
    'jackson.major': '2',
    'jackson.minor': str(random.randint(10, 17)),
    'jackson.patch': str(random.randint(0, 3)),
    'jackson.version': '${jackson.major}.${jackson.minor}.${jackson.patch}',
    'auto.minor': str(random.randint(6, 11)),
    'auto.version': '1.${auto.minor}',
    'guava.version': '%d.%d-jre' % (random.randint(28, 33), random.randint(0, 1)),
    'slf4j.version': ver(),
    'junit.version': '4.%d' % random.randint(10, 13),
    'mockito.version': ver(),
    'truth.version': ver(),
    'javapoet.version': ver(),
    'errorprone.version': ver(),
}

LIBS = [
    ('com.google.guava', 'guava', '${guava.version}', None),
    ('com.fasterxml.jackson.core', 'jackson-databind', '${jackson.version}', None),
    ('com.fasterxml.jackson.core', 'jackson-core', '${jackson.version}', None),
    ('org.slf4j', 'slf4j-api', '${slf4j.version}', None),
    ('junit', 'junit', '${junit.version}', 'test'),
    ('org.mockito', 'mockito-core', '${mockito.version}', 'test'),
    ('com.google.auto.value', 'auto-value', '${auto.version}', 'provided'),
    ('com.google.auto.value', 'auto-value-annotations', '${auto.version}', None),
    ('com.google.truth', 'truth', '${truth.version}', 'test'),
    ('org.ow2.asm', 'asm', ver(), None),
    ('com.squareup', 'javapoet', '${javapoet.version}', None),
    ('com.google.errorprone', 'error_prone_annotations', '${errorprone.version}', None),
    ('com.google.code.findbugs', 'jsr305', ver(), 'provided'),
]
MANAGED = LIBS + [('com.example', 'auto-core', '${project.version}', None)]

OVR = ['jackson.minor', 'jackson.patch', 'auto.minor', 'guava.version', 'slf4j.version',
       'junit.version', 'mockito.version', 'truth.version']


def new_value(k):
    if k in ('jackson.minor', 'jackson.patch', 'auto.minor'):
        return str(random.randint(0, 19))
    if k == 'guava.version':
        return '%d.0-android' % random.randint(25, 33)
    return ver()


MODULES = [('core', None), ('api', None), ('processor', '1.4.1-SNAPSHOT'), ('testing', '1.5.0-rc1')]
HDR = '<?xml version="1.0" encoding="UTF-8"?>'
PROJ = '<project xmlns="http://maven.apache.org/POM/4.0.0">'


def dep_xml(g, a, v, s, ind):
    out = [ind + '<dependency>', ind + '  <groupId>' + g + '</groupId>',
           ind + '  <artifactId>' + a + '</artifactId>']
    if v:
        out.append(ind + '  <version>' + v + '</version>')
    if s:
        out.append(ind + '  <scope>' + s + '</scope>')
    out.append(ind + '</dependency>')
    return out


L = [HDR, PROJ, '  <modelVersion>4.0.0</modelVersion>', '  <groupId>com.example</groupId>',
     '  <artifactId>auto-parent</artifactId>', '  <version>' + PARENT_VER + '</version>',
     '  <packaging>pom</packaging>', '  <modules>']
for name, _ in MODULES:
    L.append('    <module>' + name + '</module>')
L += ['  </modules>', '  <properties>']
for k, v in props.items():
    L.append('    <%s>%s</%s>' % (k, v, k))
L += ['  </properties>', '  <dependencyManagement>', '    <dependencies>']
for g, a, v, s in MANAGED:
    L += dep_xml(g, a, v, s, '      ')
L += ['    </dependencies>', '  </dependencyManagement>', '</project>']
with open('pom.xml', 'w') as f:
    f.write('\n'.join(L) + '\n')

for name, mver in MODULES:
    mprops = {}
    for k in random.sample(OVR, random.randint(1, 3)):
        mprops[k] = new_value(k)
    mprops['module.extra.version'] = ver()
    deps = []
    for g, a, mv, sc in random.sample(LIBS, random.randint(4, 7)):
        v = None
        r = random.random()
        if r < 0.2:
            v = ver()
        elif r < 0.35:
            v = mv if mv.startswith('${') else ver()
        elif r < 0.45:
            v = '${module.extra.version}'
        s = None
        if random.random() < 0.25:
            s = random.choice(['compile', 'runtime', 'test', 'provided'])
        deps.append((g, a, v, s))
    if name != 'core':
        deps.insert(random.randint(0, len(deps)), ('com.example', 'auto-core', None, None))
    L = [HDR, PROJ, '  <modelVersion>4.0.0</modelVersion>', '  <parent>',
         '    <groupId>com.example</groupId>', '    <artifactId>auto-parent</artifactId>',
         '    <version>' + PARENT_VER + '</version>', '  </parent>',
         '  <artifactId>auto-' + name + '</artifactId>']
    if mver:
        L.append('  <version>' + mver + '</version>')
    L.append('  <properties>')
    for k, v in mprops.items():
        L.append('    <%s>%s</%s>' % (k, v, k))
    L += ['  </properties>', '  <dependencies>']
    for g, a, v, s in deps:
        L += dep_xml(g, a, v, s, '    ')
    L += ['  </dependencies>', '</project>']
    os.makedirs(name, exist_ok=True)
    with open(os.path.join(name, 'pom.xml'), 'w') as f:
        f.write('\n'.join(L) + '\n')
