import random

random.seed(9031)

BASE = [
    ("org.springframework.boot", "spring-boot-starter-web", None, None),
    ("org.springframework.boot", "spring-boot-starter-data-jpa", None, None),
    ("org.springframework.boot", "spring-boot-starter-security", None, None),
    ("org.springframework.boot", "spring-boot-starter-validation", None, None),
    ("org.springframework.boot", "spring-boot-starter-actuator", None, None),
    ("com.h2database", "h2", None, "runtime"),
    ("org.postgresql", "postgresql", None, "runtime"),
    ("org.apache.commons", "commons-lang3", "3.12.0", None),
    ("com.google.guava", "guava", "31.1-jre", None),
    ("org.mapstruct", "mapstruct", "1.5.3.Final", None),
    ("org.springframework.boot", "spring-boot-starter-test", None, "test"),
    ("org.springframework.security", "spring-security-test", None, "test"),
    ("com.fasterxml.jackson.datatype", "jackson-datatype-jsr310", None, None),
]
REMOVE = [
    ("javax.xml.bind", "jaxb-api", "2.3.1", None),
    ("com.sun.xml.bind", "jaxb-impl", "2.3.3", None),
    ("com.sun.xml.bind", "jaxb-core", "2.3.0.1", None),
    ("javax.activation", "activation", "1.1.1", None),
    ("javax.activation", "javax.activation-api", "1.2.0", None),
]
RENAME = [
    ("javax.servlet", "javax.servlet-api", "4.0.1", "provided"),
    ("javax.validation", "validation-api", "2.0.1.Final", None),
    ("javax.persistence", "javax.persistence-api", "2.2", None),
    ("javax.annotation", "javax.annotation-api", "1.3.2", None),
]

deps = random.sample(BASE, random.randint(7, 10)) + random.sample(REMOVE, random.randint(2, 4))
ren = random.sample(RENAME, random.randint(2, 3))
ren = [(g, a, v, random.choice([None, "provided"]) if a == "javax.servlet-api" else s) for g, a, v, s in ren]
deps += ren + [("io.jsonwebtoken", "jjwt", "${jjwt.version}", None)]
random.shuffle(deps)
parent = "2.7.%d" % random.randint(5, 18)
java = random.choice(["1.8", "11"])


def dep(g, a, v, s):
    x = ["        <dependency>",
         f"            <groupId>{g}</groupId>",
         f"            <artifactId>{a}</artifactId>"]
    if v:
        x.append(f"            <version>{v}</version>")
    if s:
        x.append(f"            <scope>{s}</scope>")
    x.append("        </dependency>")
    return "\n".join(x)


body = "\n".join(dep(*d) for d in deps)
pom = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>{parent}</version>
        <relativePath/>
    </parent>
    <groupId>com.example</groupId>
    <artifactId>user-service</artifactId>
    <version>1.{random.randint(0, 9)}.{random.randint(0, 20)}</version>
    <name>user-service</name>
    <properties>
        <java.version>{java}</java.version>
        <jjwt.version>0.9.1</jjwt.version>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    <dependencies>
{body}
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
"""
with open("pom.xml", "w", encoding="utf-8") as f:
    f.write(pom)
