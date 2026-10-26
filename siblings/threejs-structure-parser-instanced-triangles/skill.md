## Reference notes

Use Python’s standard-library `json` to read the input and write UTF-8 text directly; a Three.js exporter is unnecessary. Do **not** convert indexed geometry to non-indexed geometry: the OBJ must retain one vertex per input vertex for each instance.

A Three.js matrix’s 16 values are **column-major**. For `m` and a local point `(x, y, z)`, its affine transform is:

```python
X = m[0]*x + m[4]*y + m[8]*z  + m[12]
Y = m[1]*x + m[5]*y + m[9]*z  + m[13]
Z = m[2]*x + m[6]*y + m[10]*z + m[14]
```

Apply the **instance matrix first, then the mesh matrix**; this is equivalent to `mesh_matrix * instance_matrix` acting on a column vector. Retain the original coordinate axes and triangle winding.

OBJ uses `v x y z` records and `f a b c` records. Face indices are **one-based**, global across the file, and may refer to vertices written earlier. For instance number `i` (starting at zero), add `i * vertex_count + 1` to each zero-based geometry index. Format coordinates with `f"{value:.6f}"`.

Workflow: read JSON; group flat `positions` and `indices` into triples; for each instance in input order, write all transformed vertices, then all faces using that instance’s index offset. Write only the requested OBJ file, without normals or other record types.
