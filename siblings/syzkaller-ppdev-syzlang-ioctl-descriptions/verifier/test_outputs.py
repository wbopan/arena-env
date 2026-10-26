import csv
import re
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'dev_training.txt'


def rows():
    with (ROOT / 'ppdev_commands.csv').open(newline='') as f:
        return list(csv.DictReader(f))


def declarations():
    return re.findall(r'^ioctl\$[^\n]+$', OUT.read_text(), re.M)


def test_file_exists():
    assert OUT.is_file()


def test_device_and_includes():
    s = OUT.read_text()
    assert 'include <linux/ppdev.h>' in s
    assert 'include <linux/parport.h>' in s
    assert re.search(r'^resource fd_ppdev\[fd\]$', s, re.M)
    assert 'syz_open_dev$ppdev(dev ptr[in, string["/dev/parport#"]], id intptr, flags flags[open_flags]) fd_ppdev' in s


def test_frob_structure():
    s = OUT.read_text()
    assert re.search(r'ppdev_frob_struct\s*\{\s*mask\s+int8\s+val\s+int8\s*\}', s)


def test_ioctl_names_and_order():
    assert [re.match(r'ioctl\$([A-Z0-9_]+)', x).group(1) for x in declarations()] == [r['name'] for r in rows()]


def test_ioctl_signatures():
    expected = []
    for r in rows():
        name = r['name']
        line = f'ioctl${name}(fd fd_ppdev, cmd const[{name}]'
        if r['argument'] != 'none':
            typ = 'ppdev_frob_struct' if r['argument'] == 'frob' else r['argument']
            line += f", arg ptr[{r['direction']}, {typ}]"
        expected.append(line + ')')
    assert declarations() == expected
