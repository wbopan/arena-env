## Reference notes

Use Python’s standard-library `json` and `pathlib`; Three.js and `OBJExporter` are unnecessary for this JSON of boxes. Read the scene from `data["object"]` and index `data["geometries"]` by `uuid`. A mesh’s `geometry` field is a UUID reference; the matching `BoxGeometry` entry supplies its full `width`, `height`, and `depth`.

**Transforms:** each 16-number `matrix` is column-major. Carry the parent’s world matrix down the tree and compute `world = parent_world × local` at every node, including the root. For column-major arrays:

```python
def mul(a, b):
    return [
        sum(a[k*4 + row] * b[col*4 + k] for k in range(4))
        for col in range(4) for row in range(4)
    ]

def point(m, x, y, z):
    return (
        m[0]*x + m[4]*y + m[8]*z + m[12],
        m[1]*x + m[5]*y + m[9]*z + m[13],
        m[2]*x + m[6]*y + m[10]*z + m[14],
    )
```

A centered box has corners at every sign combination of `(width/2, height/2, depth/2)`. Choose a consistent order for its eight corners, then define six quads using that order and split each quad into two triangles. Apply the **mesh’s world matrix** to each corner; do not additionally transform the resulting coordinates when writing OBJ.

During recursive traversal, carry the current owning part. Replace it only when the node has `type == "Group"` and a non-empty `name`; a named `Object3D` does not replace it. Add a `Mesh` to that owner only if one exists. This naturally keeps nested parts’ meshes separate. Emit files only for owners with meshes.

OBJ uses one-based indices **within each file**. For each mesh, append eight `v x y z` lines (e.g. format coordinates with `:.9f`), then 12 `f a b c` lines whose indices include the number of vertices already written for that part. Create `/root/work/output/links`, remove pre-existing contents there so only the requested `.obj` files remain, and write `<part_name>.obj` for each non-empty part.
