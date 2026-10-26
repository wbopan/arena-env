## Reference notes

Use Python’s standard-library `json`; no Civ6 district or adjacency library is needed. The objective is the sum of tile **weights**, not an adjacency bonus.

For odd-r coordinates (odd rows shifted right), use the specified cube conversion and distance:

```python
def cube(x, y):
    cx = x - (y - (y & 1)) // 2
    return cx, -cx - y, y

def hex_distance(a, b):
    return sum(abs(u - v) for u, v in zip(cube(*a), cube(*b))) // 2
```

Read the JSON object with `json.load()`. Evaluate **only** coordinates in `candidates`. For each center, iterate the supplied `tiles` array and include a tile when its hex distance is `<= 2`; this includes the center and zero-weight tiles while excluding positions not present in the map. Sum included `weight` fields and count included tile records separately.

Choose the minimum key `(-value, y, x)` to maximize value, then prefer smaller `y`, then smaller `x`. Write a single object with `center` as `[x, y]` and integer `value` and `worked_count`, using `json.dump()` to the requested output path.
