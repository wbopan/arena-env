# Spring Boot 3 POM migration

A legacy Spring Boot 2.7 Maven descriptor is at `/root/work/pom.xml`. Produce its Spring Boot 3.2 / Java 21 version at `/root/work/pom-migrated.xml`.

The output must be a well-formed Maven POM. Keep the project coordinates, the parent groupId/artifactId, the other properties and the build section unchanged.

Apply exactly these changes:

1. The parent `<version>` becomes `3.2.0`, and the property `<java.version>` becomes `21`.
2. In the project's top-level `<dependencies>`, delete these (groupId:artifactId): `javax.xml.bind:jaxb-api`, `com.sun.xml.bind:jaxb-impl`, `com.sun.xml.bind:jaxb-core`, `javax.activation:activation`, `javax.activation:javax.activation-api`.
3. Replace `io.jsonwebtoken:jjwt`, at its position, with three consecutive dependencies:
   - `io.jsonwebtoken:jjwt-api`, version `0.12.3`, no scope
   - `io.jsonwebtoken:jjwt-impl`, version `0.12.3`, scope `runtime`
   - `io.jsonwebtoken:jjwt-jackson`, version `0.12.3`, scope `runtime`
4. Rename these to Jakarta coordinates. Drop their `<version>` (the Boot parent manages it) but keep their scope:
   - `javax.servlet:javax.servlet-api` -> `jakarta.servlet:jakarta.servlet-api`
   - `javax.validation:validation-api` -> `jakarta.validation:jakarta.validation-api`
   - `javax.persistence:javax.persistence-api` -> `jakarta.persistence:jakarta.persistence-api`
   - `javax.annotation:javax.annotation-api` -> `jakarta.annotation:jakarta.annotation-api`
5. Every other dependency keeps its groupId, artifactId, version and scope. The relative order of all remaining dependencies is preserved.

Each `<dependency>` element contains `groupId` and `artifactId`. It contains `version` and `scope` elements only when they have a value. A missing scope means `compile`.
