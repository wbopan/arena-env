## Reference notes

Use Python’s `json` and `scipy.optimize` (or `numpy`) for this **single-system, MW-based** dispatch. No bus mapping, branch data, power-flow model, `baseMVA` conversion, or reserve constraints are needed.

```python
import json

with open("/root/work/network.json") as f:
    data = json.load(f)

load = sum(float(bus[2]) for bus in data["bus"])
online = [
    (i, gen, data["gencost"][i])
    for i, gen in enumerate(data["gen"])
    if int(gen[7]) == 1
]
# i remains the original 0-based gen row; output gen_index = i + 1.
```

For each online row, `gen[9] <= P <= gen[8]` in MW. The aligned `gencost` row has quadratic coefficients `c2, c1, c0 = cost[4:7]` (model 2, NCOST 3):

- Hourly cost: `c2*P*P + c1*P + c0`.
- Marginal cost: `2*c2*P + c1`, in $/MWh.
- Minimize the **sum over online generators** subject to `sum(P) == load`. Include every online generator’s `c0` in the reported cost; exclude offline rows entirely.

Check `sum(PMIN) <= load <= sum(PMAX)` before solving. For positive quadratic coefficients, a compact dispatch approach is to find a system lambda satisfying

```python
P_i(lambda) = min(PMAX_i, max(PMIN_i, (lambda - c1_i) / (2*c2_i)))
sum(P_i(lambda)) = load
```

The sum is monotone, so bracket the marginal costs at the limits and use `scipy.optimize.brentq` when the balance changes sign. At an interior output, lambda equals that generator’s marginal cost. If coefficients are zero or the optimum has no interior generators, handle the resulting linear/degenerate case explicitly rather than dividing by zero or assuming a unique price; `scipy.optimize.minimize` with an MW balance equality and generator bounds is another option.

Calculate cost and limit labels from **unrounded** outputs. For `at_limit`, compare against each limit using `abs(P - limit) <= 0.01`; resolve any coincident-limit case consistently. Round load and outputs to 3 decimals, lambda and cost to 4. Convert values to ordinary Python `float`/`int` before `json.dump`. Check the unrounded balance and bounds before writing `/root/work/dispatch.json`.
