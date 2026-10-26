## Reference notes

Use **NumPy + SciPy** (`numpy.linalg.solve`, `scipy.linalg.expm`); QuTiP is not needed. Read JSON with `json.load`, and write CSV with `csv.writer`.

In the specified basis, define the lowering operator explicitly: `sm = np.array([[0, 1], [0, 0]], dtype=complex)` and `sp = sm.conj().T`. Do not assume a library’s similarly named spin operator uses this basis convention.

For column-major vectorization, `vec(M) = M.reshape(4, order="F")`. Then
\[
\operatorname{vec}(AMB)=(B^T\otimes A)\operatorname{vec}(M).
\]
Build the **complex** \(4\times4\) Liouvillian from
\[
\mathcal L(M)=-i[H,M]+\sum_c\left(cMc^\dagger-\tfrac12\{c^\dagger c,M\}\right),
\]
using collapse operators \(\sqrt{\gamma_{\rm down}}\,\sigma_-\) and \(\sqrt{\gamma_\phi/2}\,Z\). For example, one collapse operator contributes:
```python
cd_c = c.conj().T @ c
D = np.kron(c.conj(), c) - 0.5 * (
    np.kron(np.eye(2), cd_c) + np.kron(cd_c.T, np.eye(2))
)
```
The Hamiltonian contribution is `-1j * (np.kron(I, H) - np.kron(H.T, I))`.

Find the trace-one steady state by solving \(\mathcal L\,\mathrm{vec}(\rho)=0\) with one equation replaced by `trace(rho) == 1`. With this vectorization, the trace row is `[1, 0, 0, 1]`. Reshape the result with `order="F"`.

For each delay, propagate the **operator** `sm @ rho_ss`, without normalizing or treating it as a density matrix:
```python
v_tau = expm(L * tau) @ (sm @ rho_ss).reshape(4, order="F")
M_tau = v_tau.reshape((2, 2), order="F")
C = np.trace(sp @ M_tau)
```
Population is `np.trace((sp @ sm) @ rho_ss).real`. At zero delay, `C` equals the population, a useful convention check.

Iterate cases and delays in their JSON order. Write only the requested header and columns; format numerical fields with, for example, `f"{value:.12f}"`.
