## Reference notes

- Read the paper before coding: extract text with `pypdf`, then locate the reward definition, label-smoothed objective, and **final** `beta`, `gamma`, and `label_smoothing` values. PDF extraction can scramble equation layout, subscripts, and minus signs; inspect the surrounding text if an equation looks ambiguous.
  ```python
  from pypdf import PdfReader
  reader = PdfReader("/root/work/paper.pdf")
  for i, page in enumerate(reader.pages):
      text = page.extract_text() or ""
      if any(s in text.lower() for s in ("simpo", "label smoothing", "gamma")):
          print(i + 1, text[:6000])
  ```
  If available, `pdftotext -layout /root/work/paper.pdf -` can help preserve equation spacing.

- Use NumPy for the archive and vectorized, pairwise arithmetic:
  ```python
  import numpy as np
  with np.load("/root/work/batch.npz") as batch:
      print(batch.files)
      chosen_sum = batch["chosen_logps_sum"].astype(np.float64)
      chosen_len = batch["chosen_len"].astype(np.float64)
      # Read the rejected arrays likewise.
  ```
  Token log-probabilities are **already summed**; lengths are response-token counts. Keep arrays in their original order, use the PDF’s exact placement of length normalization, `beta`, and `gamma`, and do not reduce across pairs.

- For numerical stability, `np.logaddexp(0, -x)` computes `-log(sigmoid(x))`, while `np.logaddexp(0, x)` computes `-log(sigmoid(-x))`. Apply the PDF’s label-smoothing weights to the appropriate terms. Use natural logs; avoid forming `sigmoid` and then taking its log.

- Write with `np.savez("/root/work/loss.npz", losses=..., chosen_rewards=..., rejected_rewards=...)`. Check that all three outputs are finite `float64` arrays of identical shape `(N,)`.
