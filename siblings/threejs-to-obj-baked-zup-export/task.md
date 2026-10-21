# Bake a Three.js-style scene graph into a single Z-up OBJ

`/root/work/scene.json` is a serialized Three.js scene. It has two keys:

- `geometries`: a map from geometry id to `{"vertices": [[x,y,z],...], "faces": [[i,j,k],...]}`. Face indices are 0-based.
- `root`: the root node.

Every node has `type` (`Group` or `Mesh`), `name`, `position` [x,y,z], `rotation` [rx,ry,rz] in radians, `scale` [sx,sy,sz] and `children` (a list of nodes). Mesh nodes also have `geometry`, which is a geometry id. Meshes may have children.

Use the Three.js conventions:

- Each node's local matrix is T * R * S.
- R uses Euler order `XYZ`, so R = Rx(rx) * Ry(ry) * Rz(rz).
- A node's world matrix is parent_world * local. The root's parent is the identity.
- Points are column vectors.

Bake every mesh's world matrix into its vertices. Then convert from Three.js Y-up to Blender Z-up by applying a -90 degree rotation about X after the world transform.

Write `/root/work/object.obj` with every mesh, in depth-first pre-order: a node comes before its children, and children follow list order. For each mesh, write:

1. a line `o <mesh name>`,
2. one `v x y z` line per geometry vertex, in geometry order, with 6 decimal places,
3. one `f a b c` line per face, in geometry order.

Face indices are 1-based and global across the whole file. They are offset by the number of vertices written before this mesh.
