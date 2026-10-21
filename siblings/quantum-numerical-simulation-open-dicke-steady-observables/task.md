# Steady-state observables of a small open Dicke model

The file `/root/work/cases.csv` lists several parameter sets with these columns:

`case_id, omega0, omegac, g, kappa, gamma_down, gamma_phi, gamma_cpump`

Each case is a cavity coupled to N = 2 two-level systems.

## Model

Hamiltonian (no rotating-wave approximation):

H = omega0 Jz + omegac a^dag a + g (a + a^dag)(J+ + J-)

Definitions:

- J- = sigma-^(1) + sigma-^(2) and J+ = (J-)^dag.
- Jz = (sigma_z^(1) + sigma_z^(2))/2.
- sigma- = |g><e|, sigma_z = |e><e| - |g><g|.
- The cavity is truncated to Fock states n = 0..9 (dimension 10).
- The full Hilbert space is cavity ⊗ qubit1 ⊗ qubit2, dimension 40.

The dynamics follow the Lindblad master equation

drho/dt = -i[H, rho] + sum_k ( C_k rho C_k^dag - {C_k^dag C_k, rho}/2 )

with these collapse operators:

- sqrt(kappa) a (cavity loss);
- sqrt(gamma_down) sigma-^(i) for i = 1, 2 (local emission);
- sqrt(gamma_phi) sigma_z^(i) for i = 1, 2 (local dephasing);
- sqrt(gamma_cpump) J+ (collective pumping), included only when gamma_cpump > 0.

## What to compute

For each case, find the unique trace-one steady state rho_ss. Then compute:

- `n_photon` = Tr(rho_ss a^dag a)
- `jz` = Tr(rho_ss Jz)
- `cavity_purity` = Tr(rho_c^2), where rho_c is the cavity state after tracing out both spins

## Output

Write `/root/work/results.csv` with the header `case_id,n_photon,jz,cavity_purity`.

- Write one row per case, in the same order as `cases.csv`.
- Round values to 6 decimal places.
