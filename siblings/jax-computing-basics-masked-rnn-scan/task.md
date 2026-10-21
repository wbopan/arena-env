# Masked RNN scan over a padded batch

Inputs in `/root/work`:

- `seq.npy`: float64 array of shape (B, T, D), a batch of B input sequences padded to length T.
- `lengths.npy`: int64 array of shape (B,). This is the number of valid time steps of each sequence, with 1 <= length <= T.
- `rnn_params.npz`: float64 arrays with these keys:
  - `Wx` (D, H): input-to-hidden weights.
  - `Wh` (H, H): hidden-to-hidden weights.
  - `b` (H,): bias.
  - `h0` (B, H): initial hidden state of each sequence.

Run a vanilla tanh RNN over time, scanning each sequence independently from t = 0:

    h_t = tanh(x_t @ Wx + h_{t-1} @ Wh + b),   with h_{-1} = h0[i]

Here `x_t` is the row vector `seq[i, t]`. The products are row-vector times matrix, so `Wx` maps D to H and `Wh` maps H to H.

Masking convention: for sequence i, only time steps `t < lengths[i]` are valid. At padded positions (`t >= lengths[i]`) the output must be exactly 0.0. Padding never influences valid outputs.

Output: save the hidden-state sequence to `/root/work/hseq.npy`.

- Shape: (B, T, H).
- Dtype: float64.
- Entry `[i, t]` is `h_t` for sequence i at valid steps, and all zeros at padded steps.
- Values are not rounded. They must match the exact recurrence to within 1e-6 absolute.
