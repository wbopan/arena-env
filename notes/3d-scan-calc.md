**Goal:** read `/root/scan_data.stl` (binary STL). Keep only the largest connected component and drop the debris. Take its Material ID from the 2-byte attribute field and look up that ID's density in `/root/material_density_table.md`. Write `/root/mass_report.json` with `main_part_mass = volume * density` (float) and `material_id` (int). The result must be within 0.1%.

**Preferred tool (from the mesh-analysis skill):**
```python
import sys; sys.path.append('/root/.claude/skills/mesh-analysis/scripts')
from mesh_tool import MeshAnalyzer
r = MeshAnalyzer('/root/scan_data.stl').analyze_largest_component()
vol = r['main_part_volume']; mid = r['main_part_material_id']
```
First check that the module exists: `ls /root/.claude/skills/mesh-analysis/scripts`. You can also grep its function names rather than printing the whole file.

**Binary STL layout (needed for the fallback parser and for cross-checking):**
- 80-byte header.
- uint32 triangle count, little-endian.
- One 50-byte record per triangle:
  - normal: 3 float32
  - v1, v2, v3: 9 float32
  - attribute: uint16
- Check that the file size equals 84 + 50*N.

Parse it fast with numpy:
```python
import numpy as np, struct
d=open('/root/scan_data.stl','rb').read(); n=struct.unpack('<I',d[80:84])[0]
dt=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')])
t=np.frombuffer(d,dtype=dt,count=n,offset=84)
V=t['v'].astype(np.float64); attr=t['a']
```

**Connected components:**
- Merge identical vertices with `np.unique(V.reshape(-1,3), axis=0, return_inverse=True)`. Optionally round to about 1e-6 first.
- Union the three vertex indices of each triangle using union-find, or `scipy.sparse.csgraph.connected_components` on a vertex adjacency graph.
- Map each triangle to the component of its first vertex.
- "Largest" means the most triangles. Also check that the same component has the largest absolute volume. Debris is usually small; if the two criteria disagree, report both and take the volume-largest.

**Volume:** use the signed tetrahedron (divergence) formula over the component's triangles:
`vol = abs(sum(dot(v1, cross(v2, v3))) / 6)`.
Use float64. Take the absolute value of the total; do not sum the absolute value of each term.

**Material ID:** take the attribute values of the main component's triangles. Use `np.unique(..., return_counts=True)` and pick the most common value (it should be uniform). Debris may carry different IDs, so ignore them.

**Density table:**
- Inspect cheaply with `head -40 /root/material_density_table.md` or `wc -l`.
- Parse the markdown table rows (`|`-separated) and find the row whose ID column equals `mid`.
- Note the density units (e.g. g/cm³) and any notes in the table about units or ID mapping.

**Units pitfall:** volume comes out in STL coordinate units cubed. The skill says not to assume mm. If the density is in g/cm³ and the coordinates are in the same base unit (cm), multiply directly. Only convert if the task or table explicitly states different units (e.g. coords in mm with g/cm³ means divide the mm³ volume by 1000). The task gives no unit statement, so the default is to multiply directly, matching the skill's guidance.

**Plan (about 8 commands):**
1. `ls /root /root/.claude/skills/mesh-analysis/scripts`, then `head` the density table.
2. Check that the STL file size matches 84 + 50*N.
3. Write `/root/solve.py`:
   - Run MeshAnalyzer and get its volume and ID.
   - Independently compute both with the numpy method.
   - Print the component count, the triangle counts and volumes of the top components, and the attribute counts of the main component.
   - Look up the density and compute the mass.
   - Write the JSON.
4. Run it. If MeshAnalyzer and the numpy check disagree by more than 0.1%, investigate (likely vertex merging or the choice of largest component).
5. `cat /root/mass_report.json` and verify:
   - keys are exactly `main_part_mass` (number) and `material_id` (int);
   - values are native Python types, so cast with `float()` / `int()` before `json.dump`.

**Output:**
```python
json.dump({"main_part_mass": float(mass), "material_id": int(mid)}, open('/root/mass_report.json','w'), indent=1)
```
