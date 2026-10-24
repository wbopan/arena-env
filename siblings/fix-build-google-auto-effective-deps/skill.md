## Reference notes

Use Python standard-library `xml.etree.ElementTree`, `re`, and `json`; the task’s rules can be applied directly to the POMs without running a Maven build.

```python
from pathlib import Path
import xml.etree.ElementTree as ET

root_dir = Path("/root/work")
ns = {"m": "http://maven.apache.org/POM/4.0.0"}
parent = ET.parse(root_dir / "pom.xml").getroot()

def text(element, path):
    found = element.find(path, ns)
    return found.text.strip() if found is not None and found.text is not None else None
```

**XML paths matter:** all POM elements are namespaced. Use direct-child paths such as `m:properties`, `m:dependencies/m:dependency`, and `m:dependencyManagement/m:dependencies/m:dependency`; a broad `.//m:dependency` would also pick up managed or plugin dependencies. Read module directories from the parent’s `m:modules/m:module` elements, then open each directory’s `pom.xml`. ElementTree iteration preserves declaration order.

For each module:

- Build a property dictionary from the *parent’s direct* `<properties>` children, then update it with the module’s direct `<properties>` children. Property names are the children’s local XML tag names (strip the namespace). Set `project.version` to the module’s direct `<version>` if present, otherwise the parent’s direct `<version>`—not `<parent><version>`.
- Index the parent’s managed dependencies by `(groupId, artifactId)`. For each dependency in the module’s *own* `<dependencies>`, take its version if present, else the matching managed version. Take its scope if present, else the managed scope if present, else `"compile"`. Do not add dependencies merely because they appear in management.
- Interpolate the selected version **using that module’s effective properties**, even when the version came from parent management. A regex such as `r"\$\{([^}]+)\}"` finds references. Repeat substitution until none remain; report an unknown property or reference cycle rather than leaving `${...}` in the output.

Write a JSON object keyed by each module POM’s `artifactId`. Each dependency object must contain only `groupId`, `artifactId`, `version`, and `scope`, with string values. A compact workflow is: inspect the POM structure briefly, write one parser script, run it, then inspect the resulting JSON for module coverage, dependency order, and unresolved `${` references.
