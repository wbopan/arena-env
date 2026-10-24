## Reference notes

Use Python’s `json`, `numpy`, and `xml.etree.ElementTree`; no Three.js runtime or OBJ export is needed. The URDF only **references** `meshes/<link_name>.obj`.

- Read `json.load(file)["object"]`. Each node’s `matrix` is a **local** transform, stored as 16 column-major numbers:
  ```python
  local = np.asarray(node["matrix"], dtype=float).reshape((4, 4), order="F")
  world = parent_world @ local
  ```
  Start the traversal with `np.eye(4)`. Include every node’s transform, even for nodes that are not links.
- A link is exactly a node with `type == "Group"` and a non-empty `name`. **Do not discard empty groups** because they have no meshes. A named `Object3D` remains a container, not a link.
- During traversal, carry the nearest ancestor link (and its world matrix). When a link is encountered, record it; if an ancestor link exists, record a joint to that ancestor. Then make the current link the nearest ancestor for its descendants.
- For a child link’s joint, obtain its translation in the parent link’s frame:
  ```python
  relative = np.linalg.solve(parent_link_world, child_link_world)
  xyz = relative[:3, 3]  # round each coordinate to 4 decimals for output
  ```
  Do not use the child’s local translation directly: intervening containers can have transforms.
- Classify the **child link name**, lowercased. Check the task’s revolute substrings first, then prismatic substrings, otherwise `fixed`. The task’s name rule takes precedence over geometry-based heuristics.
- Emit all links sorted by link name, then all joints sorted by `joint_<child_name>`. Use XML escaping (e.g., `ElementTree`) for names and filenames. Match the requested `robot`, `visual/geometry/mesh`, `parent`, `child`, and `origin xyz` structure and mesh path exactly; no axis or limit is requested.
- Write to `/root/work/output/object.urdf`, creating the output directory if necessary. After writing, inspect the file and check that every recorded link appears once and every non-root link has one joint.
