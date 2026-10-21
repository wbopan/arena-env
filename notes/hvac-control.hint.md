1. Grep `hvac_simulator.py` for class, def, step, dt, reset and noise, and `ls` for config files, to learn the API without printing the file.
2. In one numpy/scipy script: run a 50 % step test (≥ 60 s, ≥ 20 points), then fit `y0+K*u*(1-exp(-t/tau))` with `curve_fit` and compute r²/RMSE.
3. Tune IMC PI with λ ≈ 20–30 s (`Kp=tau/(K*λ)`, `Ki=1/(K*λ)`, `Kd=0`) and run the closed loop for ≥ 150 s with 0–100 clamp, anti-windup and a 28 °C cutoff, resetting or cooling first if possible.
4. Write calibration_log, estimated_params, tuned_gains, control_log and metrics JSONs with exactly the example keys (overshoot as a fraction).
5. Print a short summary of the metrics against the targets and retune λ if any fail.
