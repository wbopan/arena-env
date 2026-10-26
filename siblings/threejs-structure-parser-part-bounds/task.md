# World-space bounds by part

The generated input `/root/work/scene.json` contains a Three.js-style object tree under `object`. Each node has `type`, `name`, and a local `matrix` of 16 numbers in Three.js column-major order. Nodes may have `children`. Each Mesh additionally has `positions`, a flat XYZ vertex list in its own local coordinates. All matrices are affine. The scene root is a container, not a part.

Produce exactly one output file, `/root/work/part_bounds.csv`. Its header must be `part,mesh_count,vertex_count,min_x,min_y,min_z,max_x,max_y,max_z,centroid_x,centroid_y,centroid_z`. Include one row per named Group that owns at least one Mesh, sorted by part name. A Mesh belongs to its nearest named Group ancestor; unnamed groups remain transparent, while nested named groups own their meshes separately.

For each part, transform every owned vertex through its Mesh node and all ancestors into world coordinates. Report the axis-aligned minimum and maximum across those vertices. The centroid is the arithmetic mean of all transformed vertices, counting repeated vertices if present. `mesh_count` and `vertex_count` are decimal integers. Express coordinates in scene units with exactly six digits after the decimal point. Do not convert axes or include vertices owned by child parts.
