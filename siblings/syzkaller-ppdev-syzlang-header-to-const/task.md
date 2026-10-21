You are preparing a syzkaller constants file for a new parallel-port-like character device. Its UAPI header is at `/root/work/zq.h`. There is no kernel source, so the values must be computed by hand from the header.

The header contains:
- a character-literal macro naming the ioctl type,
- struct definitions,
- ioctl macros built with `_IO`, `_IOR`, `_IOW` and `_IOWR`. The type argument is either that macro or a character literal, the number is in hex, and the size argument is a scalar C type or a `struct`,
- flag macros written in hex, decimal or `(1 << n)` form.

C comments may appear anywhere.

Write `/root/work/dev_zq.txt.const` in syzkaller `.const` format for the single architecture amd64:
- Line 1 must be exactly `arches = amd64`.
- Then add one line `NAME = VALUE` for every `#define` that has a numeric value. This includes all ioctl numbers and all flags.
- VALUE is a plain non-negative decimal integer.
- Exclude the character-literal macro and any macro defined with no value, such as the include guard.
- Sort the lines by NAME in ascending ASCII order.
- Write no other lines.

Conventions:
- Use the Linux generic ioctl encoding: `dir << 30 | size << 16 | type << 8 | nr`. The direction values are `_IO`=0, `_IOW`=1, `_IOR`=2 and `_IOWR`=3. For `_IO` the size is 0.
- `size` is `sizeof` the argument type on x86_64 (LP64).
- Scalar sizes: `char`/`unsigned char` = 1, `short`/`unsigned short` = 2, `int`/`unsigned int` = 4, `long`/`unsigned long`/`long long` = 8.
- Each scalar's alignment equals its size.
- Structs use natural C layout: each field is aligned to its own alignment, and the total size is padded to a multiple of the largest field alignment.
