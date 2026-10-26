# Wigner samples for a driven lossy cavity

The input `/root/work/cavity_cases.csv` has columns `case_id,detuning,drive,kappa,n_thermal`. Each row describes one cavity with the Fock basis truncated to the five states |0⟩ through |4⟩. The file `/root/work/phase_points.csv` has columns `point_id,x,p`; its coordinates are dimensionless canonical quadratures. Use every case with every point, in input order.

For each case, find the trace-one steady density matrix of the Lindblad master equation. Use H = detuning a†a + drive(a+a†), with collapse operators √[kappa(n_thermal+1)] a and √(kappa n_thermal) a†. The annihilation operator has matrix element ⟨n−1|a|n⟩=√n, with no states outside the specified truncation.

Evaluate the Wigner function at each supplied point. Use the convention W for the vacuum equals exp(−x²−p²)/π. Write exactly one file, `/root/work/wigner_samples.csv`, with header `case_id,point_id,x,p,wigner`. Preserve input IDs and coordinates, and write numeric values to at least nine decimal places. Do not add an index column or other rows. The output should contain one row per case–point pair.
