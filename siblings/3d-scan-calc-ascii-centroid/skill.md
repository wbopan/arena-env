## Reference notes

The supplied `MeshAnalyzer` is documented for **binary STL** and reports a largest component without establishing that “largest” means *enclosed volume*. For this ASCII STL, use the Python standard library.

- An ASCII facet has three `vertex x y z` lines. Ignore `facet normal`, `outer loop`, `solid`, and `endsolid` for geometry and grouping. Facets from different bodies may be interleaved.
- Identify a shared vertex by its three coordinate **text tokens**, e.g. `tuple(line.split()[1:4])`; convert those tokens to `float` for calculations. Do not use approximate coordinate matching.
- Build connected components with union–find: assign each facet an index; keep a dictionary from vertex-token tuple to the first facet containing it; union the current facet with that facet on every repeated vertex. After reading, group facets by their final roots. Neither facet order nor a shared edge is required.

For each component, use its outward-oriented triangles to compute signed tetrahedral contributions. Translating all vertices by one fixed origin `o` for that component improves numerical stability. For triangle vertices `a, b, c`, let `A=a-o`, `B=b-o`, `C=c-o`:

```python
v = dot(A, cross(B, C)) / 6.0       # signed volume, mm³
moment += v * (A + B + C) / 4.0     # vector first moment, mm⁴
volume += v
```

Then the solid’s centroid in mm is `o + moment / volume`. The closed, outward-oriented surface makes the total volume positive; preserve each triangle’s vertex order. This is a **solid** centroid, not the average of vertices or facet centroids. Choose the component with the greatest enclosed volume, not the most facets or vertices.

Take the selected component’s coordinate-wise bounding-box minimum and maximum over its triangle vertices. Convert its volume from mm³ to cm³ by dividing by `1000`. `debris_count` is the total component count minus one.

Workflow: inspect a few lines to confirm the ASCII layout; write one streaming parser and union–find script; accumulate properties per component, select by volume, and write JSON with only the requested keys. Round the volume to 4 decimals and each reported mm coordinate to 3 decimals; keep unrounded values for selection and intermediate calculations.
