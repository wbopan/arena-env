## Reference notes

Use a **manual `.const` file**; `syz-extract` requires kernel source. The output format is plain text: `arches = amd64` followed by `NAME = VALUE` lines, with no declarations or C syntax.

For each ioctl, use the Linux generic encoding:

```python
direction = {"_IO": 0, "_IOW": 1, "_IOR": 2, "_IOWR": 3}
value = (direction[op] << 30) | (size << 16) | (type_value << 8) | nr
```

`type_value` is `ord(character)` for a character literal, including one supplied through a macro. Parse hexadecimal ioctl numbers with `int(text, 16)`. `_IO` has size zero; the other operations use **`sizeof` the stated argument type**, not the size of an ioctl argument pointer.

On amd64 (LP64), scalar size and alignment are both: `char` 1, `short` 2, `int` 4, `long` and `long long` 8; `unsigned` does not change either. Compute structs in field order using natural alignment:

```python
def align_up(n, alignment):
    return (n + alignment - 1) // alignment * alignment

offset = 0
max_alignment = 1
for field_size, field_alignment in fields:
    offset = align_up(offset, field_alignment)
    offset += field_size
    max_alignment = max(max_alignment, field_alignment)
struct_size = align_up(offset, max_alignment)
```

For flags, parse hex and decimal literals as integers; `(1 << n)` is `1 << n`. Emit every numeric-valued `#define`, but not character-literal definitions or valueless definitions.

**Short workflow:** Read the header once; remove C comments before parsing (replace block comments with whitespace so tokens cannot accidentally join), and account for any continued preprocessor lines. Collect character-literal macros and struct sizes needed by ioctls, then calculate ioctl and flag values. Write the required first line and the numeric definitions ordered by `sorted(names)` (Python string ordering is ASCII for these macro names). Reopen the output briefly to check its line format, ordering, and that values are non-negative decimal integers.
