**Goal.** For 4 loss cases, compute the steady state of the open Dicke model (N=4 spins plus one cavity mode). Trace out the spins and compute the cavity Wigner function on x, p ∈ [-6, 6] with a 1000×1000 grid. Write the results to 1.csv, 2.csv, 3.csv and 4.csv.

**Tools.** Use QuTiP and its permutational-invariance module PIQS (`from qutip.piqs import Dicke, jspin, num_dicke_states`). First check the version:
`python -c "import qutip;print(qutip.__version__)"`
- In both QuTiP 4.7 and 5.x, PIQS lives at `qutip.piqs`.
- If the import fails, try `pip install qutip` (QuTiP 5 still ships piqs). As a last resort, `pip install qutip-piqs`.

**Spin space.** PIQS works in the Dicke basis, not in 2^N space.
- `nds = num_dicke_states(N)` gives 9 for N=4.
- `jx, jy, jz = jspin(N)`, `jp = jspin(N, "+")`, `jm = jp.dag()`. All are 9×9.
- Local (single-spin) dissipation must go through `Dicke(...)`. Do not build it by hand with sigma operators: it is not a collective operator.
- Dicke keyword names:
  - `dephasing` = γ_φ (local)
  - `pumping` = γ↑ (local)
  - `emission` = γ↓ (local)
  - `collective_pumping` = γ⇑
  - `collective_emission` = γ⇓
  - `hamiltonian` = spin Hamiltonian
- `Dicke(N, hamiltonian=w0*jz, dephasing=..., ...).liouvillian()` returns the 81×81 spin Liouvillian. Unspecified rates default to 0.

**Building the full Liouvillian.** Use the ordering photon ⊗ spin. The photon goes first, so `ptrace(rho, 0)` gives the cavity.

```python
import numpy as np
from qutip import *
from qutip.piqs import Dicke, jspin, num_dicke_states

N=4; w0=wc=1.0; kappa=1.0; g=2/np.sqrt(N); nphot=16
nds=num_dicke_states(N)
jx,jy,jz=jspin(N); jp=jspin(N,"+"); jm=jp.dag()
a=destroy(nphot)

L_phot = liouvillian(wc*a.dag()*a, [np.sqrt(kappa)*a])
I_phot = to_super(qeye(nphot)); I_tls = to_super(qeye(nds))
h_int = g*tensor(a.dag()+a, jp+jm)           # exactly the task's coupling term
L_int = -1j*spre(h_int) + 1j*spost(h_int)

cases = {1: dict(dephasing=0.01, pumping=0.1),
         2: dict(dephasing=0.01, emission=0.1),
         3: dict(dephasing=0.01, emission=0.1, collective_pumping=0.1),
         4: dict(dephasing=0.01, emission=0.1, collective_emission=0.1)}
xvec = np.linspace(-6,6,1000)
for k,kw in cases.items():
    L_tls = Dicke(N=N, hamiltonian=w0*jz, **kw).liouvillian()
    L = super_tensor(L_phot, I_tls) + super_tensor(I_phot, L_tls) + L_int
    rho = steadystate(L)
    rc = ptrace(rho, 0)                      # cavity, 16x16
    W = wigner(rc, xvec, xvec)               # shape (len(p), len(x)) = (1000,1000)
    np.savetxt(f"{k}.csv", W, delimiter=",")
    print(k, rc.tr(), expect(num(nphot), rc), W.shape, W.min(), W.max())
```

The coupling term g(a†+a)(J₊+J₋) equals 2g(a†+a)Jx. Use `jp+jm` directly; do not use `jx` alone, which would halve the coupling.

**Pitfalls**
- **Hamiltonian placement.** Pass ω₀Jz via `hamiltonian=` to Dicke. Do not add it a second time elsewhere. ω_c a†a goes in `L_phot`.
- **Superoperator dims.** `super_tensor` needs the subsystem order to match `tensor(a..., j...)`. If `L_int` dims mismatch, check that both use photon then spin.
- **steadystate on a superoperator.** `steadystate(L)` accepts the Liouvillian directly. The total space is 16·9 = 144, so L is 20736², which is sparse and fast.
- **If steadystate is slow or fails in QuTiP 5,** try `steadystate(L, method="direct")` or `method="svd"` (dense still works at this size).
- **Wigner convention.** Keep QuTiP's default `wigner(rho, xvec, yvec)` (g=√2). The rows of W correspond to p (yvec) and the columns to x (xvec). Do not transpose.
- **Wigner speed.** A 1000×1000 grid is about 1e6 points. For a 16-dimensional state this takes a few seconds per case. If it is slow, use `method='clenshaw'`.
- **CSV format.** Write a plain 1000×1000 numeric matrix with comma delimiter, no header and no index column.
- **Output location.** Write files to the working directory (normally where the task/tests expect them, e.g. /root). First check with `ls` whether an output directory is implied, and if so write there.

**Plan (few commands)**
1. `python -c "import qutip, qutip.piqs; print(qutip.__version__)"`, then `pwd; ls`.
2. Write the script above to `solve.py` with a heredoc. Run it with `python solve.py` and print only the summary lines.
3. Sanity checks:
   - trace ≈ 1;
   - ⟨n⟩ is finite and small relative to nphot (truncation is OK);
   - the Wigner integral `W.sum()*(dx**2) ≈ 1`, where dx = 12/999.
4. Verify the files with `ls -la *.csv; head -c 200 1.csv`, and check the shape with `python -c "import numpy as np;print(np.loadtxt('1.csv',delimiter=',').shape)"`.
5. Expected physics: the cases with collective emission/pumping and local pumping vs. emission give visibly different cavity distributions. If two CSVs are identical, the rates were not applied (check the kwarg names).
