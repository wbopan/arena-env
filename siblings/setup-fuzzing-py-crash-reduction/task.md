# Minimize a reproducible fuzz input

A saved fuzzer input is available at `/root/work/crash.bin`. The associated crash condition is described by `/root/work/crash_rule.json`, which contains `magic_hex` and `remainder`. Treat the crash condition as true for a byte string only when all four requirements hold: it has at least four bytes; it starts with the two bytes represented by `magic_hex`; it contains a zero byte somewhere after those first two bytes; and the sum of all its byte values modulo 11 equals `remainder`.

Find a crashing input obtained solely by deleting zero or more bytes from `crash.bin`, without reordering or changing any retained bytes. Among all such inputs, choose one with the fewest bytes. If several have that length, choose the lexicographically smallest resulting byte string. If the same byte string can be formed using multiple sets of original positions, choose the lexicographically smallest list of retained zero-based indices.

Write exactly one UTF-8 JSON file at `/root/work/minimized.json`. It must be an object with precisely these fields: `minimized_hex` (lowercase hexadecimal bytes), `length` (integer byte count), and `retained_indices` (the chosen ascending list of original zero-based positions). The result must satisfy the crash condition. Do not overwrite either input file.
