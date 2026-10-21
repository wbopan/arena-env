# Per-part geometry report for a Three.js-style scene

`/root/work/scene.json` is a serialized Three.js scene. It has two keys:

- `geometries`: a map from geometry id to `{"vertices": [[x,y,z],...], "faces": [[i,j,k],...]}`.
- `root`: the root node.

Every node has `type`, `name`, `position`, `rotation` [rx,ry,rz] in radians, `scale` and `children`. The type is one of:

- `Group`.
- `Mesh`, which has a `geometry` id.
- `InstancedMesh`, which has a `geometry` id and `instances`, a list of `{position, rotation, scale}`.

Use the Three.js conventions:

- Each node's local matrix is T * R * S, with R = Rx * Ry * Rz (Euler order XYZ).
- A node's world matrix is parent_world * local. The root's parent is the identity.
- Each instance's copy uses world = mesh_world * instance_local.

**Parts.** A part is a `Group` node with a non-empty name. Mesh names do not define parts. Each Mesh or InstancedMesh belongs to its nearest ancestor that is a part. Nested parts are separate. Meshes with no part ancestor are ignored. Skip parts that own no geometry.

**Coordinates.** Convert all baked vertices to Blender Z-up by applying a -90 degree X rotation after the world transform.

**Output.** Write `/root/work/parts.json` as `{"parts": [...]}`, sorted by name. Each entry has these fields:

- `name`
- `object_count`: geometry copies (1 per Mesh, plus 1 per instance)
- `vertex_count`: summed over copies
- `triangle_count`: summed over copies
- `bbox_min`: [x,y,z] of the part's baked Z-up vertices, rounded to 4 decimals
- `bbox_max`: [x,y,z] of the part's baked Z-up vertices, rounded to 4 decimals
