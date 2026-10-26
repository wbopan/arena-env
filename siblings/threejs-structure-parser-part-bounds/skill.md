## Reference notes

Use Python’s `json` and `csv`, plus `numpy` for affine transforms. No OBJ export, normals, triangulation, or axis conversion is needed: the JSON already contains the vertices to count.

- A named `Group` is a part; the scene root is only a container. A `Mesh` belongs to its **nearest named Group ancestor**. Unnamed groups do not change ownership, and a nested named group takes ownership of its own descendant meshes. Omit groups with no owned meshes.
- Traverse from the root while carrying both the current world matrix and the current owning group. Three.js stores each 4×4 `matrix` **column-major**; compose transforms as `parent_world @ local`, including the Mesh’s matrix.
- `positions` is a flat sequence of local `x,y,z` triples. Transform every triple, including repeats. Do not infer vertices from faces or deduplicate them.

```python
import numpy as np

local = np.asarray(node["matrix"], dtype=float).reshape((4, 4), order="F")
world = parent_world @ local

xyz = np.asarray(mesh["positions"], dtype=float).reshape((-1, 3))
homogeneous = np.column_stack((xyz, np.ones(len(xyz))))
world_xyz = (world @ homogeneous.T).T[:, :3]  # affine matrices
```

For each part, accumulate the number of owned Mesh nodes, vertex count, coordinate-wise minima and maxima, and the sum of transformed XYZ values. Divide that sum by the vertex count for the arithmetic centroid. Format each coordinate with `f"{value:.6f}"`; write counts as integers. Use `csv.writer` with the task’s exact header and rows sorted by part name.
