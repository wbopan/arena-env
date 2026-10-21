1. Grep `/app/trl/trl/trainer/{utils.py,grpo_trainer.py,grpo_config.py}` for selective_log_softmax, decode_and_strip_padding/think, the advantage std epsilon, the KL/clip loss and the ref model, and check `git diff`. Read train_grpo.py and reward_fn.py only to learn the configs and expected format.
2. Fix every bug, expecting several:
   - The log-prob must be logit minus logsumexp, ≤ 0.
   - The advantage eps must be about 1e-4, not large.
   - Plain text without think tags must pass through unchanged; an unclosed think block returns empty.
   - Loss/KL signs and the frozen ref model must be correct.
   - Config defaults must be sane.
3. Make minimal edits only; never touch train_grpo.py or reward_fn.py.
4. Verify with a small script (F.log_softmax match, nonzero advantages, decode cases) and confirm trl imports from /app/trl.
