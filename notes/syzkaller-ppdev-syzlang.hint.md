1. Grep `sys/linux` for existing ppdev/parport names, a `syz_open_dev$` example, `timeval {`, and the `.const` per-arch syntax.
2. Write one Python script that computes the 23 ppdev ioctl numbers (type 0x70; `_IOW` = 1<<30, `_IOR` = 2<<30, size<<16, nr 0x80–0x9b) and writes both files. Give timeval 16 bytes on amd64 and 8 on 386.
3. In `dev_ppdev.txt`: the two includes, `resource fd_ppdev[fd]`, `syz_open_dev$ppdev("/dev/parport#")`, ptr[in] for W and ptr[out] for R, `ppdev_frob_struct {mask int8, val int8}`, and the `ieee1284_modes`/`ppdev_flags` sets (both must be used).
4. In `dev_ppdev.txt.const`: `arches = 386, amd64` plus every used constant. Then run `make descriptions` and `make all TARGETOS=linux TARGETARCH=amd64`, tailing the output.
