# Regularized logistic regression: gradient and gradient descent

Inputs in `/root/work`:

- `data.npz`: float64 arrays with these keys:
  - `X` (N, D): features.
  - `y` (N,): labels in {-1, +1}.
  - `w0` (D,): initial weights.
- `config.json`: `{"lr": float, "steps": int, "l2": float}`.

Loss as a function of the weights w (no bias term):

    L(w) = mean_i( log(1 + exp(-y_i * (X_i . w))) ) + 0.5 * l2 * ||w||^2

Compute the following:

1. `loss_init`: L(w0).
2. `grad_init`: the exact gradient dL/dw evaluated at w0. This is a list of D floats.
3. Run full-batch gradient descent starting from w0 for exactly `steps` updates:

       w <- w - lr * dL/dw(w)

   - `w_final`: the weights after the last update, a list of D floats.
   - `loss_final`: L(w_final).
4. `train_accuracy`: the fraction of samples with sign(X_i . w_final) == y_i. Treat a score of 0 as +1.

Output: write `/root/work/result.json`.

- It is a JSON object with exactly the keys `loss_init`, `grad_init`, `w_final`, `loss_final` and `train_accuracy`.
- Use plain JSON numbers.
- Do not round. The values must be accurate to 1e-6.
- Compute log(1 + exp(.)) in a numerically stable way, because some margins are large.
