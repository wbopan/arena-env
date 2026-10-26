# Odd–even transit depth check

`/root/work/photometry.csv` has columns `time_days,flux,reference,quality,sigma`. Divide flux by reference to remove the modeled stellar variation; only quality-zero rows are usable. `sigma` is the uncertainty of this normalized flux. The separate file `/root/work/candidates.csv` lists `id,period_days,epoch_days,duration_days` for two proposed periodic signals.

For each candidate, assign an event number to every observation by rounding `(time_days-epoch_days)/period_days` to the nearest integer, with exact half-integers rounded toward positive infinity. A row belongs to that event when its distance from the event center is at most half the listed duration. Event numbers divisible by two are **even**; all others are **odd**, including negative event numbers.

Compute one shared baseline: the inverse-variance-weighted mean normalized flux of usable rows outside the event windows of **both** candidates. For each candidate, compute separate weighted mean fluxes from its odd and even event rows, excluding any row that also falls in the other candidate’s event window. Each depth is baseline minus its event mean, multiplied by one million to obtain ppm. Delta is the absolute difference between the two unrounded depths in ppm. Label a candidate `alternating` if delta is at least 2000 ppm, otherwise `consistent`.

Write `/root/work/odd_even.csv` with header `id,odd_depth_ppm,even_depth_ppm,delta_ppm,verdict`, in candidate-file order. Round each ppm value to the nearest integer; do not round before classification.
