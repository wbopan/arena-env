**Goal.** Create two files and make both build commands succeed:

- `/opt/syzkaller/sys/linux/dev_ppdev.txt` (syzlang descriptions)
- `/opt/syzkaller/sys/linux/dev_ppdev.txt.const` (constant values)

There is no kernel source in this environment, so `make extract` cannot be used. You must write the `.const` file by hand.

**Cheap inspection first (do not cat whole files).**

- Check for clashes with names that may already exist: `grep -rln "PPCLAIM\|fd_ppdev\|parport" sys/linux/ | head`. Duplicate `ioctl$PPCLAIM` or flag names cause compile errors.
- See how another device opener is written: `grep -rh "syz_open_dev\$" sys/linux/*.txt | head -3`.
- Confirm a timeval struct exists: `grep -n "^timeval {" sys/linux/*.txt`.
- See the per-arch const syntax: `head -5 sys/linux/dev_kvm.txt.const`, or any `*.const` file.
  - The usual format is `arches = 386, amd64` followed by lines like `NAME = value`.
  - When a value differs per arch it is written `NAME = amd64val, 386:386val`. Copy whatever form the existing files use.

**Ioctl encoding.** The type is `'p'` = 0x70.

- `_IO(t,nr)` = `(t<<8)|nr`
- `_IOR(t,nr,sz)` = `(2<<30)|(sz<<16)|(t<<8)|nr`
- `_IOW(t,nr,sz)` = `(1<<30)|(sz<<16)|(t<<8)|nr`

Compute every value with a small Python script; do not do the arithmetic by hand.

**The 23 non-obsolete ioctls in linux/ppdev.h.** Format: name, direction, nr, argument type.

| Ioctl | Dir | nr | Argument |
|---|---|---|---|
| PPSETMODE | W | 0x80 | int |
| PPRSTATUS | R | 0x81 | uchar |
| PPRCONTROL | R | 0x83 | uchar |
| PPWCONTROL | W | 0x84 | uchar |
| PPRDATA | R | 0x85 | uchar |
| PPWDATA | W | 0x86 | uchar |
| PPCLAIM | IO | 0x8b | none |
| PPRELEASE | IO | 0x8c | none |
| PPYIELD | IO | 0x8d | none |
| PPFCONTROL | W | 0x8e | struct ppdev_frob_struct (2 × uchar, size 2) |
| PPEXCL | IO | 0x8f | none |
| PPDATADIR | W | 0x90 | int |
| PPNEGOT | W | 0x91 | int |
| PPWCTLONIRQ | W | 0x92 | uchar |
| PPCLRIRQ | R | 0x93 | int |
| PPSETPHASE | W | 0x94 | int |
| PPGETTIME | R | 0x95 | struct timeval |
| PPSETTIME | W | 0x96 | struct timeval |
| PPGETMODES | R | 0x97 | uint |
| PPGETMODE | R | 0x98 | int |
| PPGETPHASE | R | 0x99 | int |
| PPGETFLAGS | R | 0x9a | int |
| PPSETFLAGS | W | 0x9b | int |

Notes on the table:

- Leave out PPWSTATUS, PPRECONTROL, PPWECONTROL, PPRFIFO and PPWFIFO; they are obsolete.
- Sizes: uchar = 1, int and uint = 4.
- timeval is 16 bytes on amd64 and 8 bytes on 386, so PPGETTIME and PPSETTIME need per-arch values. All other ioctls are the same on both arches.
- Sanity checks: PPCLAIM = 28811 (0x708b), PPSETMODE = 0x40047080.

**Flag values from linux/parport.h and ppdev.h.**

IEEE1284 modes:

| Flag | Value |
|---|---|
| IEEE1284_MODE_NIBBLE | 0 |
| IEEE1284_MODE_BYTE | 1 |
| IEEE1284_DEVICEID | 4 |
| IEEE1284_MODE_ECP | 16 |
| IEEE1284_MODE_ECPRLE | 48 |
| IEEE1284_MODE_EPP | 64 |
| IEEE1284_MODE_COMPAT | 256 |
| IEEE1284_MODE_BECP | 512 |
| IEEE1284_MODE_ECPSWE | 1024 |
| IEEE1284_MODE_EPPSL | 2048 |
| IEEE1284_MODE_EPPSWE | 4096 |
| IEEE1284_ADDR | 8192 |
| IEEE1284_EXT_LINK | 16384 |

Optionally add IEEE1284_DATA = 0.

ppdev flags:

| Flag | Value |
|---|---|
| PP_FASTWRITE | 4 |
| PP_FASTREAD | 8 |
| PP_W91284PIC | 16 |

**Writing dev_ppdev.txt (sketch).**

```
include <linux/ppdev.h>
include <linux/parport.h>

resource fd_ppdev[fd]

syz_open_dev$ppdev(dev ptr[in, string["/dev/parport#"]], id intptr, flags flags[open_flags]) fd_ppdev

ioctl$PPCLAIM(fd fd_ppdev, cmd const[PPCLAIM])
ioctl$PPSETMODE(fd fd_ppdev, cmd const[PPSETMODE], arg ptr[in, flags[ieee1284_modes, int32]])
ioctl$PPGETMODE(fd fd_ppdev, cmd const[PPGETMODE], arg ptr[out, int32])
ioctl$PPRSTATUS(fd fd_ppdev, cmd const[PPRSTATUS], arg ptr[out, int8])
ioctl$PPWDATA(fd fd_ppdev, cmd const[PPWDATA], arg ptr[in, int8])
ioctl$PPFCONTROL(fd fd_ppdev, cmd const[PPFCONTROL], arg ptr[in, ppdev_frob_struct])
ioctl$PPGETTIME(fd fd_ppdev, cmd const[PPGETTIME], arg ptr[out, timeval])
ioctl$PPSETTIME(fd fd_ppdev, cmd const[PPSETTIME], arg ptr[in, timeval])
ioctl$PPSETFLAGS(fd fd_ppdev, cmd const[PPSETFLAGS], arg ptr[in, flags[ppdev_flags, int32]])
ioctl$PPGETFLAGS(fd fd_ppdev, cmd const[PPGETFLAGS], arg ptr[out, int32])
... (all 23)

ppdev_frob_struct {
	mask	int8
	val	int8
}

ieee1284_modes = IEEE1284_MODE_NIBBLE, IEEE1284_MODE_BYTE, ...
ppdev_flags = PP_FASTWRITE, PP_FASTREAD, PP_W91284PIC
```

Rules for the description file:

- **Directions:** every `W` ioctl takes `ptr[in, ...]` and every `R` ioctl takes `ptr[out, ...]`. `_IO` ioctls take no argument.
- **Flag sets must be used:** the syzkaller compiler rejects unused flags, structs and resources. Use `ieee1284_modes` in PPSETMODE and PPNEGOT, and `ppdev_flags` in PPSETFLAGS.
- **Indentation:** struct fields use tab indentation.
- **open_flags:** if `open_flags` does not exist in this tree, check what other `syz_open_dev` lines use.

**Writing the .const file.**

- One `NAME = value` line per constant used in the `.txt`, in decimal, with the `arches = 386, amd64` line first.
- Every constant referenced in the `.txt` must appear, otherwise the build fails with "X is defined for none of the arches".
- Do not define constants you don't use; this is harmless but noisy.
- Generate both files from one Python script so the names and values stay consistent.

**Plan.**

1. Run the greps above (about 4 commands).
2. Write `/tmp/gen.py`. It should:
   - hold the ioctl table and compute the numbers;
   - emit the `.txt`;
   - emit the `.const` with sorted lines and the per-arch PPGETTIME/PPSETTIME values.
3. Run the script, then check the output with `grep -c '^ioctl\$PP' sys/linux/dev_ppdev.txt` (expect 23) and `head` the `.const` file.
4. Run `cd /opt/syzkaller && make descriptions 2>&1 | tail -20`.
5. Fix any reported errors: unknown type, unused flags, or a missing const.
6. Run `make all TARGETOS=linux TARGETARCH=amd64 2>&1 | tail -20` and confirm it succeeds.
