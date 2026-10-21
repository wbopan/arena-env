# GRPO log-probs and clipped surrogate loss

The directory `/root/work` contains one GRPO batch saved as NumPy `.npy` files. N is the number of completions, T the completion length and V the vocabulary size.

- `logits.npy`: float64, shape (N, T, V). Current-policy logits at each completion position.
- `tokens.npy`: int64, shape (N, T). Sampled token ids.
- `mask.npy`: int64, shape (N, T). 1 marks a real token and 0 marks padding. Ignore padded positions everywhere.
- `old_logprobs.npy` and `ref_logprobs.npy`: float64, shape (N, T). Per-token log-probs under the generating policy and under the reference policy.
- `advantages.npy`: float64, shape (N,). One advantage per completion.

Compute the following:

1. Per-token log-probs of the current policy: `logp = log_softmax(logits over V)` evaluated at the sampled token.
2. `ratio = exp(logp - old_logprob)` for each token.
3. `surr = min(ratio*A, clip(ratio, 0.8, 1.2)*A)`, where A is the completion's advantage.
4. `kl_tok = logp - ref_logprob`.
5. Per completion, take the mean of `surr` over its masked tokens and the mean of `kl_tok` over its masked tokens.
6. Average each per-completion mean over the N completions. Call the results S and K.

Write `/root/work/loss.json` with these keys:

- `seq_logprobs`: a list of N floats. Each is the sum of `logp` over that completion's masked tokens.
- `policy_loss`: equal to -S.
- `kl`: equal to K.
- `loss`: equal to `policy_loss + 0.04 * kl`.
- `clip_fraction`: the fraction of all masked tokens whose ratio is < 0.8 or > 1.2.

All values are plain floats, unrounded.
