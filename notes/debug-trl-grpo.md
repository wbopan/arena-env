**Goal:** find and fix bugs in the TRL source under `/app/trl` so GRPO training on the countdown task can improve. Never edit `/app/train_grpo.py` or `/app/reward_fn.py`. Read them only to learn which config values, completion format and tags the reward expects. Expect several planted bugs spread across pipeline stages, probably 3 or more. Stopping after one or two fixes is the classic failure. Check every stage: reward/decoding, advantages, log-probs, loss/KL/ref model, config defaults.

**Where to look (cheap inspection):**
- `wc -l /app/train_grpo.py /app/reward_fn.py; head -60 /app/train_grpo.py`: see the GRPOConfig args (num_generations, beta, epsilon, lr) and whether the reward needs `<answer>` tags or similar.
- `cd /app/trl; git status; git diff | head -200`: if it is a git repo, a diff may reveal the edits directly. Also try `git log --oneline | head`.
- Find the key functions with grep rather than reading whole files:
  `grep -n "def selective_log_softmax\|def decode_and_strip_padding\|think" trl/trainer/utils.py`
  `grep -n "std_grouped\|mean_grouped\|advantages\s*=\|1e\|epsilon\|beta\|per_token_kl\|torch.clamp\|requires_grad\|ref_model\|logsumexp" trl/trainer/grpo_trainer.py`
  `grep -n "epsilon\|beta\|num_generations\|temperature" trl/trainer/grpo_config.py`
- Print only the relevant ranges, e.g. `sed -n 'START,ENDp' file`.

**Invariants to check (correct versions):**

1. **Advantages.**
   ```
   mean = rewards.view(-1,G).mean(1).repeat_interleave(G,0)
   std  = rewards.view(-1,G).std(1).repeat_interleave(G,0)
   adv  = (rewards - mean) / (std + 1e-4)
   ```
   - The epsilon must satisfy 0 < eps << 1 (1e-4 to 1e-8). Watch for `1e4`, `1.0`, or a copy-pasted large constant. Replace the constant; keep the epsilon term.
   - The grouping must use `num_generations`, and the broadcast must be `repeat_interleave`, not `repeat`.
   - Signs: `rewards - mean`, not the reverse.
   - If scale_rewards logic exists, keep its branches.

2. **selective_log_softmax.** It must equal `F.log_softmax(logits,-1).gather(-1, index.unsqueeze(-1)).squeeze(-1)`, with values ≤ 0.
   - The correct fast path is `torch.gather(logits, -1, index.unsqueeze(-1)).squeeze(-1) - torch.logsumexp(logits, -1)`. The order must be selected logit **minus** logsumexp.
   - The bf16/fp16 branch loops over rows with `F.log_softmax(row_logits, -1)` then gathers.
   - Look for a reversed subtraction, a wrong gather dim, or a missing unsqueeze.
   - Near-one-hot check: logits `[10,0,0]` at index 0 should give ≈ -9e-5.

3. **decode_and_strip_padding** (reasoning-tag handling). Required behavior:
   - Plain text with no markers: returned unchanged after the pad strip.
   - `<think>...</think>answer`: return `text.split("</think>",1)[-1].strip()`.
   - Unclosed `<think>...`: return `""`.
   - Nested tags: keep everything after the first `</think>`.
   - Pads and special pad tokens are removed.
   - The typical bug blanks plain text, i.e. returns `""` whenever `</think>` is absent, even with no `<think>`. Fix only the broken branch; do not collapse the function to a one-liner.

4. **Loss.**
   - `ratio = exp(logp - old_logp)`.
   - `coef_1 = ratio`, `coef_2 = clamp(ratio, 1-eps, 1+eps)`.
   - `loss = -min(coef_1*A, coef_2*A)`, masked mean.
   - KL uses k3: `per_token_kl = exp(ref - logp) - (ref - logp) - 1`, so KL ≥ 0. Then `loss += beta*kl`.
   - Watch for sign flips (`+min`, `logp - ref` inside the exp), the advantage sign, a missing `unsqueeze(1)` on advantages, the wrong mask, and `.detach()` on the current logp, which kills gradient. `old_logp` may legitimately be `logp.detach()`.
   - The ref model must be frozen (`requires_grad=False`, eval mode, `torch.no_grad`) and must be a distinct object from the policy.

5. **Config defaults** (grpo_config.py), compared against the training script:
   - epsilon clip ≈ 0.2
   - beta ≈ 0.04 or smaller
   - num_generations > 2
   - temperature ≈ 0.7–1.0
   - Check that the default learning_rate is not absurd and the advantage epsilon is not huge.

**Plan:**
1. Inspect the training script, reward function, and git diff with head/grep, about 5 commands.
2. Locate each function above and print only its lines.
3. Fix each bug with a targeted `python - <<'EOF'` string replace or `sed -i`. Make minimal edits.
4. Write `/tmp/check.py` covering:
   - `selective_log_softmax` vs `F.log_softmax`: assert allclose, max ≤ 0, and the one-hot check.
   - The advantage formula on rewards `[1,0,0.5,0]` with G=4: assert max |A| > 0.1.
   - `decode_and_strip_padding` on the plain, closed-think, unclosed-think and nested cases. Use the model's tokenizer from train_grpo.py if available locally; otherwise use a small mock tokenizer whose `batch_decode` returns given strings.
   - The reward function on a correct vs a wrong countdown answer.
5. If the skill script `scripts/verify_pipeline.py` exists, run it (find it with `find / -name verify_pipeline.py 2>/dev/null`) and inspect lines marked `?`.
6. Make sure `/app/trl` is the installed package: `python -c "import trl;print(trl.__file__)"`. If it is not, run `pip install -e /app/trl` (no deps) if needed.
7. Optionally run a very short training sanity check only if it is cheap. Do not print large logs; use `| tail`.

**Output:** the fixed source files in place under `/app/trl`, with no other deliverables. Training and reward scripts stay untouched. Keep the library importable: run `python -c "import trl.trainer.grpo_trainer"` after the edits.
