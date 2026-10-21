# Quadrotor motor allocation with saturation

`/root/work/system_params.yaml` contains these parameters:

- `mass` and `gravity`
- `cT`: thrust coefficient, N/rpm^2
- `cQ`: torque coefficient, N*m/rpm^2
- `arm_length`: arm length d, in m
- `rpm_min` and `rpm_max`

`/root/work/commands.csv` has columns `id,F,Mx,My,Mz`. These are the desired total thrust (N) and body moments (N*m).

The X-frame allocation matrix A maps squared motor speeds `s = [w1^2, w2^2, w3^2, w4^2]` to `[F, Mx, My, Mz]`:

- row F: `cT, cT, cT, cT`
- row Mx: `0, d*cT, 0, -d*cT`
- row My: `-d*cT, 0, d*cT, 0`
- row Mz: `-cQ, cQ, -cQ, cQ`

For each command:

1. Solve `A s = [F, Mx, My, Mz]` for s.
2. Set any negative entries of s to 0.
3. Take the square root to get the unconstrained rpm of each motor.
4. Clip to `[rpm_min, rpm_max]` to get the motor rpm.
5. Compute the actually produced `[F, Mx, My, Mz] = A (rpm^2)`, using the clipped rpm.

A command is saturated if any motor's unconstrained rpm is strictly below `rpm_min` or strictly above `rpm_max`.

Write `/root/work/motor_output.csv` with the header `id,rpm1,rpm2,rpm3,rpm4,F_act,Mx_act,My_act,Mz_act,saturated`. Include one row per command, in ascending id order. Round rpm values to 3 decimals and forces/moments to 6 decimals. Write `saturated` as the integer 0 or 1.
