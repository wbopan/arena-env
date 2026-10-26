## Reference notes

Use **NumPy and SciPy**; QuTiP is not among the libraries specified as available. The five-state truncation means `a` is a \(5\times5\) matrix with `a[n-1,n] = sqrt(n)` for `n=1,...,4`; do not add transitions beyond \(|4\rangle\).

**Steady state.** With column-major vectorization (`reshape(-1, order="F")`), construct the Lindblad matrix from \(H\) and each collapse operator \(C\):
```python
I = np.eye(5)
L = -1j * (np.kron(I, H) - np.kron(H.T, I))
for C in collapse_ops:
    M = C.conj().T @ C
    L += (np.kron(C.conj(), C)
          - 0.5 * np.kron(I, M)
          - 0.5 * np.kron(M.T, I))
```
Solve \(L\,\mathrm{vec}(\rho)=0\) with \(\mathrm{Tr}\rho=1\): replace one equation with a trace row (ones at the column-major indices of diagonal elements), set its right-hand side to 1, and use `np.linalg.solve`. Reshape the answer with `order="F"`. Use collapse operators scaled by the **square roots** of their rates.

**Wigner convention.** Put \(\beta=\sqrt{2}(x+ip)\), \(P_{nn}=(-1)^n\). Then
\[
W(x,p)=\frac{1}{\pi}\operatorname{Tr}\!\left[\rho D(\beta)P\right],
\]
where the *infinite-oscillator* displacement matrix elements needed for \(0\le m,n<5\) are
\[
D_{mn}(\beta)=e^{-|\beta|^2/2}
\begin{cases}
\sqrt{n!/m!}\,\beta^{m-n}L_n^{(m-n)}(|\beta|^2),&m\ge n,\\
\sqrt{m!/n!}\,(-\beta^*)^{n-m}L_m^{(n-m)}(|\beta|^2),&m<n.
\end{cases}
\]
Use `scipy.special.eval_genlaguerre(degree, order, abs(beta)**2)` and `math.factorial`. In array form the trace is `np.trace(rho @ D @ np.diag([(-1)**n for n in range(5)]))`; take its real part after numerical evaluation. **Do not** compute `D` by exponentiating the truncated \(5\times5\) ladder operators: that changes its matrix elements. The formula gives \(e^{-x^2-p^2}/\pi\) for vacuum.

**CSV workflow.** Read both files in their existing order with `csv.DictReader`; keep IDs and coordinate strings for output, converting coordinates and case parameters to `float` only for calculations. Solve once per case, then evaluate every point in point-file order. Write with `csv.DictWriter` (or `csv.writer`), exactly the requested header and no index; format Wigner values with, for example, `f"{value:.16e}"` to retain small nonzero values. Check row count, ordering, trace, and the vacuum normalization before finishing.
