# Named-group inventory

The input `/root/work/scene.json` is a small Three.js Object3D JSON scene. Its tree starts at the `object` key; nodes have a `type`, a `name`, and optionally `children`. Mesh nodes also have a `geometry` identifier. The input is generated for this task, so use the file rather than assuming a particular hierarchy or set of names.

Write exactly one output file: `/root/work/group_inventory.json`. It must be UTF-8 JSON with two top-level fields: `groups` and `unowned_meshes`. `groups` is an array sorted by group name. Include every node whose type is `Group` and whose name is nonempty, including groups that own no meshes. Each entry has exactly these fields: `name` (string), `parent` (the nearest named ancestor Group's name, or null), and `meshes` (an array of mesh names sorted lexicographically).

Assign each Mesh to its nearest named ancestor Group. Unnamed groups and other containers do not interrupt the search; a nested named group does. Put meshes with no named Group ancestor in `unowned_meshes`, sorted lexicographically. Count each mesh once. Names in this input are unique, and neither transforms nor geometry identifiers affect ownership.
