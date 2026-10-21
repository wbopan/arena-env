import os
import xml.etree.ElementTree as ET

import pytest

IN = "/root/work/pom.xml"
OUT = "/root/work/pom-migrated.xml"
REMOVED = {("javax.xml.bind", "jaxb-api"), ("com.sun.xml.bind", "jaxb-impl"),
           ("com.sun.xml.bind", "jaxb-core"), ("javax.activation", "activation"),
           ("javax.activation", "javax.activation-api")}
RENAMED = {
    ("javax.servlet", "javax.servlet-api"): ("jakarta.servlet", "jakarta.servlet-api"),
    ("javax.validation", "validation-api"): ("jakarta.validation", "jakarta.validation-api"),
    ("javax.persistence", "javax.persistence-api"): ("jakarta.persistence", "jakarta.persistence-api"),
    ("javax.annotation", "javax.annotation-api"): ("jakarta.annotation", "jakarta.annotation-api"),
}


def load(path):
    root = ET.parse(path).getroot()
    for el in root.iter():
        if isinstance(el.tag, str) and "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]
    return root


def txt(el, tag):
    v = el.findtext(tag)
    if v is None:
        return None
    v = v.strip()
    return v or None


def deps(root):
    out = []
    for d in root.find("dependencies").findall("dependency"):
        out.append((txt(d, "groupId"), txt(d, "artifactId"), txt(d, "version"),
                    txt(d, "scope") or "compile"))
    return out


def expected_deps(orig):
    exp = []
    for g, a, v, s in deps(orig):
        if (g, a) in REMOVED:
            continue
        if (g, a) == ("io.jsonwebtoken", "jjwt"):
            exp += [("io.jsonwebtoken", "jjwt-api", "0.12.3", "compile"),
                    ("io.jsonwebtoken", "jjwt-impl", "0.12.3", "runtime"),
                    ("io.jsonwebtoken", "jjwt-jackson", "0.12.3", "runtime")]
        elif (g, a) in RENAMED:
            ng, na = RENAMED[(g, a)]
            exp.append((ng, na, None, s))
        else:
            exp.append((g, a, v, s))
    return exp


@pytest.fixture(scope="module")
def orig():
    return load(IN)


@pytest.fixture(scope="module")
def out():
    assert os.path.exists(OUT), "pom-migrated.xml missing"
    return load(OUT)


def test_parent_and_java(out):
    assert txt(out.find("parent"), "version") == "3.2.0"
    assert txt(out.find("properties"), "java.version") == "21"


def test_coordinates_preserved(orig, out):
    for tag in ["groupId", "artifactId", "version"]:
        assert txt(out, tag) == txt(orig, tag)
    for tag in ["groupId", "artifactId"]:
        assert txt(out.find("parent"), tag) == txt(orig.find("parent"), tag)


def test_no_legacy_coordinates(out):
    for g, a, _v, _s in deps(out):
        assert (g, a) not in REMOVED, f"{g}:{a} should be removed"
        assert (g, a) not in RENAMED, f"{g}:{a} should be renamed"
        assert (g, a) != ("io.jsonwebtoken", "jjwt")


def test_dependency_set(orig, out):
    assert sorted(deps(out), key=str) == sorted(expected_deps(orig), key=str)


def test_dependency_order(orig, out):
    assert deps(out) == expected_deps(orig)
