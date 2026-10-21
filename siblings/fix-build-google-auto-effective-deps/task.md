# Effective dependency versions in a multi-module Maven build

A multi-module Maven project lives in `/root/work`. The parent (aggregator) POM is `/root/work/pom.xml`. Each `<module>` entry in its `<modules>` section names a directory under `/root/work` that contains that module's `pom.xml`. All POMs use the standard namespace `http://maven.apache.org/POM/4.0.0`.

For every module, compute the effective coordinates of each dependency declared in the module's own `<dependencies>` section. Use these Maven rules:

- **Effective properties.** A module's effective properties are the parent's `<properties>`, overridden by the module's own `<properties>`. Add `project.version`, which is the module's own `<version>` if it declares one, otherwise the parent's `<version>`.
- **Version.** Use the dependency's own `<version>` if present. Otherwise use the version from the parent's `<dependencyManagement>` entry with the same groupId and artifactId.
- **Scope.** Use the dependency's own `<scope>` if present. Otherwise use the managed entry's scope. Otherwise use `compile`.
- **Interpolation.** Replace every `${name}` reference in a version using the module's effective properties. Repeat until no references remain, because property values may themselves contain references. Interpolation always happens in the module's context, including for versions inherited from the parent's dependencyManagement.

Write `/root/work/effective-deps.json` as a JSON object with this layout:

- Keys are the modules' `artifactId` values.
- Each value is an array of the module's dependencies, in declaration order.
- Each array element is an object with exactly the keys `groupId`, `artifactId`, `version` and `scope`.
- All values are strings, and every version is fully resolved, with no `${` remaining.
