## Reference notes

Use Python’s standard-library `xml.etree.ElementTree` for this POM. Maven POMs commonly declare a **default XML namespace**; unqualified lookups such as `root.find("dependencies")` will then miss elements. Read the namespace from the root tag and qualify every lookup. Register the default namespace before writing to avoid `ns0:` prefixes.

```python
import xml.etree.ElementTree as ET

tree = ET.parse("/root/work/pom.xml")
root = tree.getroot()
ns = root.tag.partition("}")[0][1:] if root.tag.startswith("{") else ""
q = lambda name: f"{{{ns}}}{name}" if ns else name
if ns:
    ET.register_namespace("", ns)

parent = root.find(q("parent"))
properties = root.find(q("properties"))
dependencies = root.find(q("dependencies"))  # project's direct child, not build/plugin dependencies

def text(element, name):
    child = element.find(q(name))
    return child.text.strip() if child is not None and child.text else None

# For each direct dependency: key = (text(dep, "groupId"), text(dep, "artifactId"))
# Modify/remove only requested nodes; insert replacements at the original index.
# tree.write(output_path, encoding="utf-8", xml_declaration=True)
```

`Element.remove(child)` removes a dependency; `Element.insert(index, child)` preserves the replacement position. For a renamed dependency, change its `groupId` and `artifactId` children, remove its `version` child, and leave its `scope` child untouched. For new dependencies, add `version` and `scope` elements only when they have values; omitted scope means Maven’s default `compile`.

Migration context from the supplied skills: Spring Boot 3 uses Jakarta EE coordinates for the specified servlet, validation, persistence and annotation APIs. The old JAXB/activation dependencies listed in the task are removed, not automatically replaced. The modular JJWT coordinates are `jjwt-api` (no scope), `jjwt-impl` (`runtime`) and `jjwt-jackson` (`runtime`).

Inspect the input’s root namespace and direct dependency list, make the requested XML edits in one script, write the separate output file, then parse that output again to confirm it is well-formed and inspect the resulting dependency order. Do not apply broader Java-source, security, Hibernate or HTTP-client migrations to this POM task.
