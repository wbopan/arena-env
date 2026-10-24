## Reference notes

Use Python’s `json` and `numpy`; this input is already a serialized scene, so Three.js, OBJ export, normals, and face-index expansion are unnecessary.

**Transforms.** Use 4×4 homogeneous matrices and column vectors. For each node (and each instance), build `local = T @ Rx @ Ry @ Rz @ S`; then `world = parent_world @ local`. For an instance, use `mesh_world @ instance_local`. Do not reverse the Euler multiplication order.

```python
import numpy as np

def local_matrix(position, rotation, scale):
    x, y, z = rotation
    cx, sx = np.cos(x), np.sin(x)
    cy, sy = np.cos(y), np.sin(y)
    cz, sz = np.cos(z), np.sin(z)
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    m = np.eye(4)
    m[:3, :3] = (rx @ ry @ rz) @ np.diag(scale)
    m[:3, 3] = position
    return m
```

Transform vertices with homogeneous coordinates (`[x,y,z,1]`). **After** the world transform, convert Y-up to Blender Z-up using the −90° X rotation: `(x, y, z) → (x, z, -y)`. Compute minima/maxima across *all transformed copies* in a part, then round only the final bounds to four decimals.

**Ownership and counts.** During a recursive walk, carry the nearest named `Group` as the current part; replace it upon entering another named `Group`. A mesh’s own name has no effect. Ignore geometry outside any part. Count one copy for a `Mesh`, and one per entry in an `InstancedMesh.instances` list. For each copy, add `len(geometry["vertices"])` and `len(geometry["faces"])`; face indices define triangles but do not change the vertex count. Omit parts with no owned copies. Sort output entries by name.

**Short workflow.** Inspect the JSON structure briefly; write one script that loads it, walks from `root` with an identity parent matrix, accumulates each part’s counts and vertex bounds, and writes `{"parts": [...]}` with `json.dump`. Run it, then check that the output parses, entries are name-sorted, and each emitted bounding box has three finite coordinates.
