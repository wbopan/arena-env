# URDF articulation from a Three.js JSON scene

`/root/work/scene.json` is a Three.js object serialized with `Object3D.toJSON()` (JSON Object format 4). The scene tree is under the `"object"` key. Every node has `type`, `name`, `matrix` (16 numbers, column-major, the local transform relative to its parent) and, optionally, `children`.

Build a minimal URDF using these rules:
- Every node of type `Group` with a non-empty name is a link. Named `Object3D` nodes are not links.
- Exactly one link has no link ancestor; it is the root link.
- Every other link gets one joint, named `joint_<child_name>`. The joint's parent is the child's nearest ancestor that is a link; unnamed groups and any `Object3D` nodes in between are skipped.
- The joint type comes from the child link name (case-insensitive substring match):
  - if it contains any of `hinge, wheel, knob, spin, rotate`, the type is `revolute`;
  - otherwise, if it contains any of `slide, slider, rail, drawer, track`, the type is `prismatic`;
  - otherwise, the type is `fixed`.
- The joint origin `xyz` is the translation part of inverse(W_parent) * W_child. W is the world matrix: the product of the local matrices from the root (included) down to the node. Round to 4 decimals.

Write `/root/work/output/object.urdf`:

```xml
<?xml version="1.0"?>
<robot name="object">
  <link name="L"><visual><geometry><mesh filename="meshes/L.obj"/></geometry></visual></link>
  <joint name="joint_C" type="T"><parent link="P"/><child link="C"/><origin xyz="x y z"/></joint>
</robot>
```

List all `<link>` elements first, sorted by name. Then list all `<joint>` elements, sorted by name.
