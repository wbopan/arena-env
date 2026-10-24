## Reference notes

- The provided `MeshAnalyzer` documents only `analyze_largest_component()`, which is insufficient when **every** component, including debris, needs a row. Parse the binary STL directly with NumPy.
- Read the 80-byte header and little-endian triangle count (`struct.unpack('<I', ...)`). Each following record is exactly 50 bytes: 12 bytes normal, 36 bytes for three `float32` vertices, then a little-endian `uint16` attribute. Here that attribute is the Material ID. A record dtype is:
  ```python
  record_dtype = np.dtype([
      ('normal', '<f4', (3,)),
      ('vertices', '<f4', (3, 3)),
      ('material', '<u2'),
  ])
  assert record_dtype.itemsize == 50
  ```
  Check that the file contains the declared number of records.

- Components connect through **any shared vertex**, not just a shared edge. Since equality is bit-identical, key vertices by their raw 12-byte coordinate representation rather than a rounded position or distance tolerance:
  ```python
  xyz = np.ascontiguousarray(records['vertices'].reshape(-1, 3))
  keys = xyz.view('V12').ravel()
  _, vertex_ids = np.unique(keys, return_inverse=True)
  triangle_vertex_ids = vertex_ids.reshape(-1, 3)
  ```
  A union-find over triangle indices can associate each vertex ID with its first triangle, then union that triangle with every other triangle using the vertex. Group triangles by final root.

- For a triangle with vertices `a, b, c`, area is `0.5 * ||cross(b-a, c-a)||`. For each **closed, consistently oriented component**, signed enclosed volume is the sum of `dot(a-o, cross(b-o, c-o)) / 6`; take the absolute value **after summing the component**. An origin `o` near that component (for example, its bounding-box centre) improves numerical stability. Do not sum absolute per-triangle volumes.
- STL coordinates are mm: `volume_cm3 = volume_mm3 / 1000`, so `mass_g = volume_mm3 / 1000 * density_g_cm3`. Inspect `materials.md` to determine its table layout and map Material IDs to densities; do not assume row order matches IDs.
- Practical flow: inspect the material table and STL record count; parse records; build vertex-based components; compute each component’s geometry and material; sort by **unrounded** volume descending; then assign ranks and write the specified CSV header. Round only when writing (`.3f` for volume and area, `.4f` for mass); use integer fields for rank, ID and triangle count.
