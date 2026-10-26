## Reference notes

Use Python’s standard-library `json` and `xml.etree.ElementTree`; this task does **not** require Three.js or OBJ export. The `geometry` identifier is not used to construct the mesh filename.

- Traverse `children` recursively, carrying the nearest named `Group` ancestor. An unnamed group leaves that ancestor unchanged.
- Assign each `Mesh` to that carried group. A named group becomes a link only if at least one mesh is assigned **directly** to it; meshes under child named groups belong to those children.
- For a link’s joint, use its nearest named `Group` ancestor as parent and the child group’s explicit `motion` value as joint type. Do not infer motion from names.
- Sort retained links by exact name. Emit all links before joints; sort joints by exact child name.
- Use `xml.etree.ElementTree` to escape names correctly, then write UTF-8 XML.

```python
import json
import xml.etree.ElementTree as ET

with open("/root/work/scene.json", encoding="utf-8") as f:
    root = json.load(f)

# During traversal, record each named group's nearest named-group
# ancestor, its motion, and how many meshes are assigned directly to it.
# Recurse through node.get("children", []).
```

URDF element conventions:

```python
robot = ET.Element("robot", name="assembly")

link = ET.SubElement(robot, "link", name=link_name)
visual = ET.SubElement(link, "visual")
geometry = ET.SubElement(visual, "geometry")
ET.SubElement(geometry, "mesh", filename=f"meshes/{link_name}.obj")

joint = ET.SubElement(robot, "joint",
                      name=f"joint_{child_name}", type=child_motion)
ET.SubElement(joint, "parent", link=parent_name)
ET.SubElement(joint, "child", link=child_name)

ET.ElementTree(robot).write(
    "/root/work/assembly.urdf", encoding="utf-8", xml_declaration=True
)
```

After writing, parse the XML once with `ET.parse(...)` and check the link and joint ordering and references.
