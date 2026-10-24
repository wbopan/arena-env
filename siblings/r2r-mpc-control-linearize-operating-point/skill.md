## Reference notes

Use Python’s `json` to read and write the files and NumPy for matrices and eigenvalues. The relevant linearization convention is \(A_c=\partial f/\partial x\), \(B_c=\partial f/\partial u\), evaluated at the reference state and input. Use the **Euler** discretization specified in the task, not a matrix exponential.

For zero-based Python index `i`, state column `i` is \(T_i\) and column `n+i` is \(v_i\). The steady-state tension equation can be rearranged and solved in order:
\[
v_i=\frac{EA-T_{i-1}}{EA-T_i}\,v_{i-1}.
\]
Start with the fixed inlet values \(v_0\) and \(T_0=0\). Then obtain each torque from its zero-acceleration equation, using \(T_{n+1}=0\).

The nonzero entries of each continuous-time Jacobian row are:

| Row | State/input column | Derivative |
|---|---|---|
| \(\dot T_i\) | \(T_i\) | \(-v_i/L_i\) |
| | \(T_{i-1}\), if \(i>1\) | \(v_{i-1}/L_i\) |
| | \(v_i\) | \((EA-T_i)/L_i\) |
| | \(v_{i-1}\), if \(i>1\) | \((T_{i-1}-EA)/L_i\) |
| \(\dot v_i\) | \(T_i\) | \(-R^2/J_i\) |
| | \(T_{i+1}\), if \(i<n\) | \(R^2/J_i\) |
| | \(v_i\) | \(-fb/J_i\) |
| \(B_c\), row \(\dot v_i\) | \(u_i\) | \(R/J_i\) |

The inlet and outlet boundary values are **constants**, so they contribute no Jacobian columns. Initialize zero arrays of shapes `(2*n, 2*n)` and `(2*n, n)`, then fill only these entries.

```python
import json
import numpy as np

with open("/root/work/system_config.json") as f:
    cfg = json.load(f)

# ... construct reference values and continuous Jacobians ...
A = np.eye(2*n) + dt * A_c
B = dt * B_c
rho = float(np.max(np.abs(np.linalg.eigvals(A))))

# Convert NumPy arrays with .tolist() and NumPy scalars with float()
# before passing the result dictionary to json.dump().
```

Keep ordinary floating-point results unrounded. Check array dimensions and that substituting the reference values into both continuous dynamics gives values near zero before writing the JSON file.
