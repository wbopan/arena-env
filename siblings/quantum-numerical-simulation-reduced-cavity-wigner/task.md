# Cavity Wigner function from a joint cavity-qubit state

The file `/root/work/rho_real.csv` holds the real part and `/root/work/rho_imag.csv` holds the imaginary part of a 16x16 density matrix. Both files are comma-separated with no header. The matrix describes a cavity mode, truncated to Fock states n = 0..7, coupled to one qubit.

The tensor order is cavity first, qubit second. Basis index k corresponds to cavity Fock state n = k // 2 and qubit state s = k % 2.

## What to compute

1. Trace out the qubit to obtain the 8x8 reduced cavity density matrix.
2. Evaluate the cavity Wigner function on a square grid. Use x = linspace(-3, 3, 31) and p = linspace(-3, 3, 31), for 961 points in total.

## Convention

Use alpha = (x + i p)/sqrt(2). The Wigner function is

W(x, p) = (1/pi) Tr[ rho_c D(alpha) Parity D(alpha)^dagger ]

where D is the displacement operator and Parity = (-1)^(a^dagger a). With this convention:

- the vacuum gives W = exp(-x^2 - p^2)/pi;
- the integral of W over dx dp is 1.

This is the same convention as QuTiP's `wigner` with its default g = sqrt(2). Evaluate the displacement exactly; do not let Fock-space truncation distort it.

## Output

Write `/root/work/wigner.csv` with the header `x,p,W` and 961 data rows.

- Order the rows with x as the outer loop (slowest varying) and p as the inner loop, both ascending.
- W must be a real number written with at least 8 significant digits.
