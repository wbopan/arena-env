1. `ls` the skill scripts dir and `head` `/root/material_density_table.md`.
2. Use `MeshAnalyzer('/root/scan_data.stl').analyze_largest_component()` from `/root/.claude/skills/mesh-analysis/scripts` for volume and material ID. Cross-check with a numpy parse: 50-byte records, uint16 attribute, vertex-merge, union-find, signed-tetra volume.
3. Look up the density for that ID and compute mass = volume × density (multiply directly unless units are stated to differ).
4. Write `{"main_part_mass": float, "material_id": int}` to `/root/mass_report.json`, then `cat` it to verify.
