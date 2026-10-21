# Per-part OBJ export from a Three.js JSON scene

`/root/work/scene.json` is a Three.js object serialized with `Object3D.toJSON()` (JSON Object format 4). The scene tree is under the `"object"` key. Every node has `type`, `name`, `matrix` (16 numbers, column-major, the local transform relative to its parent) and, optionally, `children`. `Mesh` nodes reference an entry of `"geometries"` by `uuid`. Every geometry is a `BoxGeometry` centered at its local origin, with full extent `width` (x), `height` (y) and `depth` (z).

Partition the object into parts using these rules:
- A part is a node of type `Group` with a non-empty name. Named `Object3D` nodes are not parts.
- Each mesh belongs to its nearest ancestor that is a part.
- Nested parts are separate parts. Never merge a child part's meshes into its parent.
- Meshes with no part ancestor are ignored.
- A part that owns no mesh produces no output.

A node's world matrix is the product of the local matrices of all its ancestors, from the root (included) down to the node itself.

For every part, write `/root/work/output/links/<part_name>.obj` as a text Wavefront OBJ file. For each box mesh the part owns, the file contains:
- the box's 8 world-space corner vertices, as `v x y z` lines with at least 6 decimals;
- the box's 12 triangle faces, as `f a b c` lines, where a, b and c are 1-based indices into that file's vertex list.

The directory must contain only these `.obj` files.
