1. Read `simpo_trainer.py` (grep `simpo_loss`, `gamma`, `beta`, `loss_type`), the unit test, and requirements/environment.yml; then set up a matching Python env and install the pinned deps.
2. Implement `logits = (chosen_logps - rejected_logps) - gamma_beta_ratio` and `losses = -logsigmoid(beta*logits)*(1-ls) - logsigmoid(-beta*logits)*ls`; the hinge variant is `relu(1 - beta*logits)`. Rewards are `beta*logps.detach()`; the logps are already length-averaged, so add no reference model and no extra normalization.
3. Run `cd /root/SimPO && python unit_test/unit_test_1.py`, then confirm `/root/loss.npz` has key `losses` with finite values.
4. Save `python -VV` and `python -m pip freeze` to `/root/python_info.txt`.
