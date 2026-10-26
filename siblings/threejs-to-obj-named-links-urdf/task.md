# Describe named Three.js groups as URDF links

`/root/work/scene.json` contains a small scene graph. Every node has `type`, `name`, and `children`; nodes of type `Mesh` additionally have a `geometry` identifier. The root is an unnamed container. A node of type `Group` with a nonempty name represents a candidate robot link. A mesh belongs to its nearest named Group ancestor, even when unnamed groups intervene. A named group with no meshes assigned directly to it is not a link. Child named groups do not contribute meshes to their parents.

Write one file, `/root/work/assembly.urdf`, as UTF-8 XML. Its root must be `<robot name="assembly">`. For each link, add a `<link name="...">` with one `<visual><geometry><mesh filename="meshes/NAME.obj" /></geometry></visual>`; replace `NAME` with the link's exact name. List links in alphabetical name order.

For every link except the top-level link, add one `<joint name="joint_CHILD" type="KIND">` with `<parent link="PARENT"/>` and `<child link="CHILD"/>`. The parent is the nearest named Group ancestor. `KIND` is the child's `motion` value, which is explicitly one of `fixed`, `revolute`, or `prismatic`; do not infer it from its name. List joints in alphabetical child-name order, after all links. No origins, axes, limits, inertial elements, OBJ files, or other output files are requested.
