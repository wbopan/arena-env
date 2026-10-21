# Linearize a Roll-to-Roll Web Line at its Operating Point

The file `/root/work/system_config.json` describes an n-section roll-to-roll line. It contains `n_sections`, `EA`, `R`, `fb`, `dt`, `v0`, per-section lists `L` and `J`, and the reference tensions `T_ref`. All quantities are in SI units.

The state is x = [T1..Tn, v1..vn] and the input is u = [u1..un] (motor torques). Indices i run from 1 to n. The continuous dynamics are:

- dT_i/dt = (EA/L_i)(v_i - v_{i-1}) + (1/L_i)(v_{i-1} T_{i-1} - v_i T_i)
- dv_i/dt = (R^2/J_i)(T_{i+1} - T_i) + (R/J_i) u_i - (fb/J_i) v_i

Boundary conventions: v_0 = `v0` and T_0 = 0 are fixed inlet constants, not states. T_{n+1} = 0.

Compute the following:

1. The steady-state velocities `v_ref`. Set every dT_i/dt = 0 with T_i = T_ref_i, solving sequentially from section 1.
2. The steady-state torques `u_ref`, from dv_i/dt = 0.
3. The Jacobians A_c = df/dx and B_c = df/du at (T_ref, v_ref).
4. The Euler discretization A = I + dt*A_c and B = dt*B_c.
5. The spectral radius of A, which is the maximum absolute eigenvalue.

Write `/root/work/linearization.json` with these keys:

- `v_ref`: list of n floats
- `u_ref`: list of n floats
- `A_matrix`: 2n x 2n nested list, rows first
- `B_matrix`: 2n x n nested list
- `spectral_radius`: float

Report full floating-point precision and do not round.
