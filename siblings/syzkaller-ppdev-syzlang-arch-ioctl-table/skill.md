## Reference notes

Use Python’s standard-library `csv` module; no kernel headers or syzkaller tools are needed. `csv.DictReader` reads rows in file order, and `csv.DictWriter(..., fieldnames=['name', '386', 'amd64'])` controls the output header and column order. Open CSV files with `newline=''`.

Linux ioctl encoding for the supplied fields:

```python
direction_code = {'IO': 0, 'IOW': 1, 'IOR': 2, 'IOWR': 3}
request = (direction_code[direction] << 30) | (size << 16) | (ioctl_type << 8) | nr
```

Parse `type` and `nr` as hexadecimal integers with `int(text, 16)`. Parse each `size_...` field as a **decimal byte count** with `int(text, 10)`; use the matching architecture’s size for each calculation. `_IO` uses direction code zero, but still follow the supplied encoding formula. Python integers are not signed 32-bit integers, so writing the resulting nonnegative integer as a CSV value produces unsigned decimal text.

Short workflow: inspect the CSV header and a few rows; iterate once over its rows, calculate both values, and write each name unchanged in the same order. Write the header once, with no index or extra columns. Then inspect the output header, row count, and a few rows.
