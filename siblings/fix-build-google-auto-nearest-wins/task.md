# Maven nearest-wins dependency mediation

## Inputs

- `/root/work/pom.xml` declares the direct dependencies of an application. It uses the namespace `http://maven.apache.org/POM/4.0.0`.
- `/root/work/repository.json` is a local metadata repository. It is a JSON object that maps each coordinate `groupId:artifactId:version` to the list of that artifact's own dependencies, in declaration order. Each list element has the form `{"coord": "groupId:artifactId:version", "optional": true|false}`. Every referenced coordinate exists in the repository.

## What to compute

Resolve the transitive dependency graph the way Maven mediates version conflicts: the nearest definition wins, and the first declaration breaks ties. Use exactly this procedure:

1. Start a FIFO queue with the root POM's direct dependencies, in declaration order, each at depth 1. Direct dependencies are always included, even if the POM marks them `<optional>`.
2. Pop the front entry. If its `groupId:artifactId` has already been resolved, discard the entry and do not expand it. Otherwise:
   - record its version and depth;
   - append its repository dependencies, in listed order, at depth + 1, skipping any with `optional` = true.
3. Repeat until the queue is empty.

## Output

Write `/root/work/resolved.txt` with one line per resolved artifact. Exclude the root project itself.

- Line format: `groupId:artifactId:version depth`, with a single space before the integer depth.
- Sort lines in ascending plain string order of `groupId:artifactId`.
- No header and no blank lines.
