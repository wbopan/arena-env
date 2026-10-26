# Steady-state fluorescence correlations

`/root/work/fluorescence_cases.json` supplies a `delays` array and a `cases` array. Each case has `case_id`, `detuning`, `rabi`, `gamma_down`, and `gamma_phi`. Rates, detuning, and Rabi frequency have units of inverse time; delays have units of time. Analyze each case separately in its listed order.

For one two-level emitter, use basis |0⟩, |1⟩, where Z=diag(1,−1), X=[[0,1],[1,0]], σ−=|0⟩⟨1|, and σ+=σ−†. The Hamiltonian is H=(detuning Z+rabi X)/2. Lindblad collapse operators are √gamma_down σ− and √(gamma_phi/2) Z. Find the trace-one steady state ρss. For every listed nonnegative delay τ, calculate the unnormalized first-order fluorescence correlation C(τ)=Tr[σ+ exp(Lτ)(σ−ρss)], where L is the same Lindblad generator. In particular, do not normalize C by the excited-state population or replace σ−ρss with a density matrix.

Create exactly `/root/work/fluorescence.csv`, with header `case_id,delay,population,c_real,c_imag`. `population` is the steady-state expectation Tr(σ+σ−ρss), repeated for each delay of that case. `c_real` and `c_imag` are the real and imaginary parts of C. Preserve case and delay order. Write numerical fields with at least nine decimal places and no extra columns.
