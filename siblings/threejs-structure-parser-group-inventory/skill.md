## Reference notes

Use Python’s standard-library `json`; this is a scene-tree inventory, not a geometry export. Read the root node from `json.load(... )["object"]`. Nodes may have no `children`, so iterate over `node.get("children", [])`.

- A **named group** has `type == "Group"` and a nonempty `name`. Include it even when its mesh list is empty.
- Its `parent` is the nearest *named Group* above it, not necessarily its immediate tree parent.
- A node with `type == "Mesh"` belongs to the nearest named Group **ancestor**. Unnamed groups and other containers leave that owner unchanged. A nested named group becomes the owner for meshes below it.
- Record the mesh’s `name`; `geometry` and transforms do not affect ownership. Visit each node once so each mesh is counted once.
- Sort `groups` by group name and each `meshes` array and `unowned_meshes` lexicographically. Unlike the export examples, **do not filter out empty groups**.

A depth-first traversal can carry the current named-group owner:

```python
def visit(node, owner):
    kind = node.get("type")
    name = node.get("name", "")

    if kind == "Group" and name:
        # Register group with parent=owner; then set owner=name
        ...
    elif kind == "Mesh":
        # Append name to owner's mesh list, or to unowned_meshes
        ...

    for child in node.get("children", []):
        visit(child, owner)
```

Write one UTF-8 JSON object with only the top-level fields `groups` and `unowned_meshes`; each group entry has exactly `name`, `parent`, and `meshes`. Python’s `json.dump(..., ensure_ascii=False)` preserves names as UTF-8 when the output file is opened with `encoding="utf-8"`.
