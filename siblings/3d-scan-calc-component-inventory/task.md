A build-plate scan containing several printed parts and some stray debris is stored in `/root/work/build_plate.stl`. It is a binary STL: an 80-byte header, a little-endian uint32 triangle count, then 50-byte records (normal, 3 vertices, uint16 attribute). Coordinates are in millimetres. The 2-byte attribute field of every triangle holds the **Material ID** of the body the triangle belongs to. Material densities are listed in `/root/work/materials.md`, in g/cm³.

Split the mesh into connected components. Two triangles belong to the same component if they share a vertex, applied transitively. Shared vertices have bit-identical coordinates. Every component is a closed, consistently oriented surface, and all triangles of one component carry the same Material ID.

For every component compute:
- `triangles`: number of triangles
- `volume_mm3`: enclosed volume, in mm³
- `area_mm2`: total surface area, in mm²
- `mass_g`: mass in grams, equal to the volume converted to cm³ multiplied by the density of the component's material

Write `/root/work/components.csv` with this exact header line:

`rank,material_id,triangles,volume_mm3,area_mm2,mass_g`

Include one row per component, debris included. Sort the rows by volume in descending order, with `rank` starting at 1. Round `volume_mm3` and `area_mm2` to 3 decimals and `mass_g` to 4 decimals. Write integers for `rank`, `material_id` and `triangles`. Numeric values are accepted within 0.1% relative error, with a small absolute allowance for tiny debris values.
