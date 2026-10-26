## Reference notes

Use Python’s standard library (`csv`, `re`, `json`, `pathlib`); no syzkaller build or kernel headers are needed for this audit.

- Read the inventory with `csv.DictReader(f)`. Its `name` and `direction` fields supply the authoritative expected direction.
- In syzlang, `ioctl$NAME` identifies the command, `cmd const[NAME]` references its constant, and `arg ptr[DIRECTION, int32]` specifies the pointer direction (`in`, `out`, or `inout`). Each declaration is on one line, so match declarations line by line. For example, a regex can capture the suffix and direction with `ioctl\$(?P<name>\w+).*?arg ptr\[(?P<direction>\w+),\s*int32\]`.
- In the companion `.const` file, parse `NAME = DECIMAL_VALUE` assignments. Ignore empty lines, comment lines, and the `arches = ...` assignment; `arches` is metadata, not a constant. Values are irrelevant to this comparison.
- Compare **sets of names** for missing and unused constants. Compare each declaration’s captured direction with the CSV direction for mismatches. Use `sorted(...)` for both name lists and sort mismatch records by `name`.
- Write one JSON object using `json.dump(...)` with exactly the three requested fields. Each mismatch record must contain exactly `name`, `expected` (CSV), and `actual` (syzlang).
