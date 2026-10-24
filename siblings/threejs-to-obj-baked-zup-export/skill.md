## Reference notes

Use Python’s `json` and `numpy`; the input is already serialized geometry, so a Three.js exporter is unnecessary.

```python
import json
import numpy as np

with open("/root/work/scene.json") as f:
    scene = json.load(f)
```

Use **column vectors** and 4×4 homogeneous matrices. For each node, construct `local = T @ Rx @ Ry @ Rz @ S` from its position, rotation (radians), and scale. Its `world = parent_world @ local`; start at `np.eye(4)`. In particular, Euler `XYZ` here means `Rx @ Ry @ Rz`, **not** the reverse order.

For angles `a, b, c`, the 3×3 rotation blocks are:

```text
Rx(a) = [[1, 0, 0], [0, cos(a), -sin(a)], [0, sin(a), cos(a)]]
Ry(b) = [[cos(b), 0, sin(b)], [0, 1, 0], [-sin(b), 0, cos(b)]]
Rz(c) = [[cos(c), -sin(c), 0], [sin(c), cos(c), 0], [0, 0, 1]]
```

For a mesh vertex, compute `world @ [x, y, z, 1]`, then rotate **afterward** by −90° about X. That axis conversion maps `(x, y, z)` to `(x, z, -y)` in world coordinates. Do not apply it separately at every graph level.

Traverse recursively in **depth-first pre-order**: process the current node if it is a `Mesh`, then visit `children` in list order. Visit children of meshes too. Look up a mesh’s vertex and face arrays via `scene["geometries"][node["geometry"]]`.

OBJ details:

- Write `o <name>`, followed by that mesh’s `v` lines and then its `f` lines; keep the source array orders.
- Format coordinates with `f"{value:.6f}"`.
- OBJ vertex indices are **1-based and global**. For each face index `i`, write `i + vertices_written_before_this_mesh + 1`. Increment that running vertex count by the mesh’s number of vertices afterward.
- Faces remain triangles in their given index order; no normals, geometry merging, or per-group exports are needed.
