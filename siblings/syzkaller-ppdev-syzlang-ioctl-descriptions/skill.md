## Reference notes

Use Python’s standard-library `csv.DictReader` to preserve the CSV row order and the spelling of `name`:

```python
import csv

with open("/root/work/ppdev_commands.csv", newline="") as f:
    rows = list(csv.DictReader(f))
```

Syzlang syntax needed here:

```text
resource resource_name[fd]

struct_name {
    field_name int8
}

ioctl$CMD(fd fd_type, cmd const[CMD])
ioctl$CMD(fd fd_type, cmd const[CMD], arg ptr[in, int32])
```

- A structure’s fields appear in declaration order. Define the `frob` structure before declarations that use it.
- Pointer directions are `in`, `out`, and `inout`; use each row’s `direction` verbatim. `none` means **omit the entire third argument**, not `ptr[none, ...]`.
- For `frob`, use the structure’s name as the type inside `ptr[...]`; for `int8` and `int32`, use the CSV type directly.
- `const[NAME]` uses the symbolic command name. There is no need to calculate ioctl numbers or create a `.const` file for this requested output.
- Build the text in memory, then write **only** `/root/work/dev_training.txt` once. Check that the output has one `ioctl$` declaration per input row, in CSV order, with no extras.
