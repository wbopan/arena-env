# Reproduce the SimPO loss from a paper excerpt

You are reproducing the loss computation of an NLP paper. The relevant excerpt of the paper is at `/root/work/paper.pdf`. It defines the length-normalized implicit reward, the label-smoothed SimPO objective, and the final hyperparameters (`beta`, `gamma`, `label_smoothing`). Use exactly the formula and hyperparameter values given in the PDF.

Input batch: `/root/work/batch.npz` contains four 1-D arrays of equal length N:
- `chosen_logps_sum`: summed token log-probabilities of the chosen (preferred) response under the policy
- `rejected_logps_sum`: summed token log-probabilities of the rejected response
- `chosen_len`, `rejected_len`: number of response tokens of each response

Index i of every array belongs to the same preference pair.

For every pair compute the chosen reward, the rejected reward and the per-example SimPO loss (no reduction / no averaging over the batch).

Output: save a NumPy archive to `/root/work/loss.npz` with these keys, each a float64 array of shape (N,) in the original pair order:
- `losses`: per-example loss
- `chosen_rewards`: reward of the chosen response
- `rejected_rewards`: reward of the rejected response

Natural logarithms are used throughout. Values must match a reference implementation within a relative tolerance of 1e-5.
