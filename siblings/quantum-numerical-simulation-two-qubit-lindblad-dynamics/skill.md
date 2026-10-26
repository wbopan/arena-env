## Reference notes

Use `json` and `csv` from the standard library, plus NumPy and `scipy.linalg.expm`. A **matrix exponential** evaluates the time-independent Lindblad evolution at each requested time independently, so input times need not be sorted or unique.

In the ordered basis \(|00\rangle,|01\rangle,|10\rangle,|11\rangle\), build two-qubit operators with `np.kron(first_qubit_operator, second_qubit_operator)`. Define the lowering operator explicitly as `np.array([[0, 1], [0, 0]], dtype=complex)`; this fixes its action as \(|0\rangle\langle1|\). The initial density matrix is the outer product of the basis vector at index `2` with itself.

For a collapse operator \(C\), the master equation is
\[
\dot\rho=-i(H\rho-\rho H^\dagger)
 +\sum_C\left(C\rho C^\dagger-\tfrac12(C^\dagger C\rho+\rho C^\dagger C)\right).
\]
Use the task’s specified square-root factors on **each** collapse operator, including \(\sqrt{\gamma_\phi/2}\) for dephasing. The exchange term retains its specified factor of \(1/2\).

A compact propagation pattern (with `H`, `c_ops`, and `rho0` constructed per run) is:

```python
import numpy as np
from scipy.linalg import expm

ident = np.eye(4, dtype=complex)
L = -1j * (np.kron(ident, H) - np.kron(H.T, ident))
for C in c_ops:
    D = C.conj().T @ C
    L += np.kron(C.conj(), C)
    L -= 0.5 * (np.kron(ident, D) + np.kron(D.T, ident))

v0 = rho0.reshape(16, order="F")
# At t == 0, use rho0 directly; otherwise:
rho_t = (expm(L * t) @ v0).reshape((4, 4), order="F")
```

The `order="F"` on **both** reshapes is essential: the displayed Kronecker-product Liouvillian uses column-major vectorization. An alternative is `scipy.integrate.solve_ivp` on the matrix-valued master equation, but its `t_eval` requires sorted times; preserve the input order when writing rows.

For each density matrix, compute \(z_1=\operatorname{Tr}[(Z\otimes I)\rho]\) and \(z_2=\operatorname{Tr}[(I\otimes Z)\rho]\). Trace out qubit two to obtain \((\rho_1)_{ac}=\sum_b\rho_{ab,cb}\); for example:

```python
rho1 = np.einsum("abcb->ac", rho_t.reshape(2, 2, 2, 2))
purity1 = np.trace(rho1 @ rho1).real
```

Take `.real` on expectation values to discard tiny floating-point imaginary residuals. Iterate runs and times in their original JSON order. Write the exact requested CSV header with `csv.writer`, no index, and format numeric fields with at least nine decimal places (for example, `f"{value:.12f}"`).
