`/root/work/part.stl` is an ASCII STL of a scanned part, with coordinates in millimetres. Besides the part itself, the file contains small pieces of scanning debris. The facets of all bodies are interleaved in arbitrary order.

Each body is a closed surface with consistent outward orientation: vertex order is counter-clockwise when seen from outside. A vertex shared between facets is written with identical text in every facet.

Split the facets into connected components. Facets that share a vertex belong to the same component, applied transitively. The **main part** is the component with the largest enclosed volume. Every other component counts as debris.

For the main part, compute:
- its enclosed volume, in cm³
- its centroid, in mm: the centre of mass of the solid assuming uniform density, not the average of its vertices
- its axis-aligned bounding box, in mm

Write `/root/work/part_props.json` with exactly these keys:

```json
{
  "volume_cm3": 3.1416,
  "centroid_mm": [x, y, z],
  "bbox_min_mm": [xmin, ymin, zmin],
  "bbox_max_mm": [xmax, ymax, zmax],
  "debris_count": 4
}
```

Round `volume_cm3` to 4 decimals and all mm coordinates to 3 decimals. `debris_count` is the integer number of components other than the main part.

Accepted tolerances:
- volume: 0.1% relative
- centroid: 0.01 mm
- bounding box: 0.002 mm
